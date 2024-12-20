import pandas as pd
import os
import logging
from tqdm import tqdm
from aux_extract_pdf import process_pdf
from transformers import AutoModelForCausalLM, AutoTokenizer

#base_path = '/media/pablo/windows_files/00 - Master/05 - Research&Thesis/R2-Research_Internship_2/02-data/pdfs/'
#output_path = '/media/pablo/windows_files/00 - Master/05 - Research&Thesis/R2-Research_Internship_2/02-data/pdfs_txt/'
base_path = "../02-data/pdfs/"
output_path = "../02-data/txts/"

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def process_folder(input_folder_path, output_folder_path):
    """
    Transcribes all PDFs within the input folder and saves the transcribed text
    in the corresponding output folder with the same file structure.

    Args:
        input_folder (str): The root folder containing labeled PDF files.
        output_folder (str): The destination folder for the transcribed text files.

    Raises:
        OSError: If there is an issue reading or writing files or directories.
    """
    try:

        pdf_files = [f for f in os.listdir(input_folder_path) if f.endswith(".pdf")]

        for pdf_file in tqdm(pdf_files, desc="Processing PDFs", unit="file"):

            pdf_path = os.path.join(input_folder_path, pdf_file) # /02-data/pdfs/label_x/pdf_file_y.pdf
            pdf_name = os.path.splitext(pdf_file)[0]  # pdf_file_y

            process_pdf(pdf_name, pdf_path, output_folder_path,**model_kwargs)

            logging.debug(f"Transcribed PDF saved at: {output_folder_path}")


    except OSError as e:
        logging.debug(f"File system error: {str(e)}")
    except Exception as e:
        logging.debug(f"Unexpected error during transcription: {str(e)}")

def compare_folders(input_folder, output_folder):
    """
    Compares the number of documents in each corresponding folder within
    the input and output directories. If the number of documents doesn't match,
    calls the 'save_transcribed_pdfs' function to process the label.

    Args:
        input_folder (str): The root directory containing the original PDF files. # /pdfs/
        output_folder (str): The directory containing the transcribed text files. # /pdfs_txt/
    
    Returns:
        None: Logs results of the comparison.
    """
    try:
        for label in os.listdir(input_folder):
            input_path = os.path.join(input_folder, label)    # /pdfs/label1/
            output_path = os.path.join(output_folder, label)  # /txts/label1/

            if os.path.isdir(input_path):
                # if output does not exist, create it
                if not os.path.exists(output_path):
                    os.makedirs(output_path)
                    logging.debug(f"Created output folder: {output_path}")

                # Count PDF and TXT files
                pdfs_count = len([f for f in os.listdir(input_path) if f.endswith(".pdf")])
                pdfs_txt_count = len([f for f in os.listdir(output_path) if f.endswith(".txt")])

                # Compare counts, and process if not matching
                if pdfs_count != pdfs_txt_count: # dosent make sense if each image is its own separate file
                    logging.info(f"Processing '{label}'")
                    process_folder(input_path, output_path)
                else:
                    logging.info(f"Folder '{label}': PDF and TXT file counts match ({pdfs_count}). (not really, check condition)")
            else:
                logging.warning(f"'{input_path}' is not a valid folder. Skipping...")

    except OSError as e:
        logging.error(f"File system error during folder comparison: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error during folder comparison: {str(e)}")


def load_model(table_gpt):
    model_name = table_gpt
    # Another configuration at x10 parameters "tablegpt/TableGPT2-72B"

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    example_prompt_template = """Given access to a pandas dataframes, answer the user question.

    /*
    "{var_name}.head(5).to_string(index=False)" as follows:
    {df_info}
    */

    Question: {user_question}
    """
    question = "Provide a detail description for each of the rows"

    # Return all arguments as a dictionary
    return {
        "model": model,
        "tokenizer": tokenizer,
        "prompt_template": example_prompt_template,
        "question": question,
    }

table_gpt = "tablegpt/TableGPT2-7B"
model_kwargs = load_model(table_gpt)

compare_folders(base_path, output_path)
#process_folder(base_path, output_path)