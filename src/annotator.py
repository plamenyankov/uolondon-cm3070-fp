import ast
import pandas as pd
import sys
from dotenv import load_dotenv
import openai
import os
load_dotenv()
class Annotator:
    def __init__(self, prompt_source):
        load_dotenv()
        self.prompt_source = prompt_source
        # Retrieve the API key from environment variables
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.openai = openai
        self.openai.api_key = self.get_api_key()

    def get_api_key(self):
        return self.api_key
    def print_progress_bar(self, iteration, total, bar_length=50):
        """
        Print a progress bar to the console.

        Parameters:
        - iteration (int): the current iteration (0-indexed)
        - total (int): total number of iterations
        - bar_length (int): length of the progress bar, default is 50
        """

        progress = (iteration + 1) / total
        arrow = '=' * int(round(progress * bar_length) - 1) + '>'
        spaces = ' ' * (bar_length - len(arrow))

        sys.stdout.write(f'\r[{arrow + spaces}] {int(progress * 100)}%')
        sys.stdout.flush()  # Flush the output buffer
    #  Annotation with OpenAi API
    def load_data_source(self, source):
        """
        Load data from a source file
        :param source:
        :return: data
        """
        return pd.read_csv(source)

    def get_completion(self, prompt, model="gpt-4-0125-preview"):
        # Get completion from OpenAI API.
        messages = [
            {"role": "system", "content": "Act like annotator that labels the sentiment of youtube comments"},
            {"role": "user", "content": prompt}]
        try:
            response = self.openai.chat.completions.create(model=model,
                                                           messages=messages,
                                                           temperature=0)
        except TimeoutError:  # replace with the specific exception for OpenAI timeout
            print("Timeout error")
            return ""
        except Exception as ex:
            print(f"Error processing comment {ex}")
            return ""

        return response.choices[0].message.content
    def annotate_comments(self, data, prompt_id, output_file="data/annotated/annotations_final.csv", input_file="data/preprocessed/fe_data.csv"):
        # Check if annotations file exists and load existing annotations
        try:
            existing_annotations = pd.read_csv(output_file)
        except FileNotFoundError:
            existing_annotations = pd.DataFrame(columns=['index', 'usyk_sentiment', 'fury_sentiment'])
            existing_annotations.to_csv(output_file, index=False)

        # get prompt by index from prompts.csv
        prompts = self.load_data_source(self.prompt_source)
        prompt = prompts.loc[prompt_id, 'prompt']
        total_comments = data.shape[0]
        count = 0

        for i, comment in data.iterrows():
            # Skip if annotation already exists
            if i in existing_annotations['index'].values:
                continue

            complete_prompt = f"""
                 {prompt}         
                Response Example:
                {{   
                "usyk_sentiment": "sentiment",
                "fury_sentiment": "sentiment"
                }}

               Comment:
                {comment['comment']}            
               """
            try:
                response = self.get_completion(complete_prompt)
                actual_dict = ast.literal_eval(response)
                # Write the annotation to the file
                with open(output_file, "a") as f:
                    f.write(f"{i},{actual_dict['usyk_sentiment']},{actual_dict['fury_sentiment']}\n")
            except TimeoutError:  # replace with the specific exception for OpenAI timeout
                continue
            except Exception as ex:
                print(f"Error processing comment {i}: {ex}")
                continue

            # Update and print the progress bar after each iteration
            self.print_progress_bar(count, total_comments)
            count += 1

        # Reload all annotations and merge
        annotations_df = pd.read_csv(output_file)
        clean_data = pd.read_csv(input_file)
        merged_df = pd.merge(clean_data, annotations_df, left_index=True, right_on='index', how='inner').set_index('index')
        merged_df.index.name = ''

        return merged_df









