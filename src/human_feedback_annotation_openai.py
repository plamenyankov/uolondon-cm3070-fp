import ast
import pandas as pd
import sys
from dotenv import load_dotenv
from openai import OpenAI
import os
load_dotenv()
class HFAnnotator:
    def __init__(self, comments_source, annotations_source, prompt_source, accuracy_source, prompt_id=0):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.openai = OpenAI(api_key=self.api_key)
        self.comments = self.load_comments(comments_source)
        self.prompt_source = prompt_source
        self.annotations_source = annotations_source
        self.accuracy_source = accuracy_source
        self.prompt_id = prompt_id
        self.batch_start = 30
        self.batch_end = 40


    def get_completion(self, prompt, model="gpt-4-0125-preview"):
        # Get completion from OpenAI API.
        messages = [
            {"role":"system", "content":"Act like annotator that labels the sentiment of youtube comments"},
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
    def load_comments(self, comments_source):
        """
        Load batches of comments from the comments source
        :return: comments
        """
        df = pd.read_csv(comments_source)
        # df = df[df['category'] == 'fury_usyk'].loc[:, ['clean_comment']].reset_index()
        df = df[df['category'] == 'fury_usyk'].loc[:, ['comment']].reset_index()
        return df

    def load_data_source(self, source):
        """
        Load data from a source file
        :param source:
        :return: data
        """
        return pd.read_csv(source)


    def get_next_batch(self):
        """
        Get the next batch of comments from the comments source
        :return: comments
        """
        return self.comments.iloc[self.batch_start:self.batch_end]

    def openai_annotate(self):
        """
        Annotate a batch of comments using OpenAI's API.
        Use the prompt_id to get the prompt from prompts.csv.

        :param comment:
        :param prompt_id:
        :return: indexes, comments, usyk_sentiment, fury_sentiment
        """

        # get prompt by index from prompts.csv
        prompts = self.load_data_source(self.prompt_source)
        prompt = prompts.loc[self.prompt_id, 'prompt']
        comments = self.get_next_batch()

        openai_annotations = []
        total_comments = comments.shape[0]
        count = 0

        for i, comment in comments.iterrows():

            openai_prompt = f"""
                {prompt}         
                Response Example:
                {{   
                "usyk_sentiment": "sentiment",
                "fury_sentiment": "sentiment"
                }}

               Comment:
                {comment['comment']}
                """
            # {comment['clean_comment']}

            try:
                response = self.get_completion(openai_prompt)
                actual_dict = ast.literal_eval(response)
                annotations_dict = {
                    'prompt_id': self.prompt_id,
                    'index': comment['index'],
                    # 'comment': comment['clean_comment'],
                    'comment': comment['comment'],
                    'usyk_sentiment': actual_dict['usyk_sentiment'],
                    'fury_sentiment': actual_dict['fury_sentiment']
                }
                openai_annotations.append(annotations_dict)
            except Exception as ex:
                print(f"Error processing comment {i}: {ex}")
                return response
            # Update and print the progress bar after each iteration
            self.print_progress_bar(count, total_comments)
            count += 1
        return openai_annotations

    def check_existing_annotations(self, comments):
        """
        Check if the comments have already been human annotated.
        Get comments indexes from the comments DataFrame.
        Load the annotations from the human_annotations.csv file.
        Check if the comment index is in the annotations DataFrame.
        :param comments:
        :return: boolean
        """
        df = pd.DataFrame(comments)
        indexes = df['index'].tolist()
        annotations = self.load_data_source(self.annotations_source)

        for index in indexes:
            if index not in annotations['index'].tolist():
                return False
        return True

    def convert_digit_to_sentiment(self, digit):
        if digit == '':
            return 'neutral'
        digit = int(digit)
        if digit == 0:
            return 'negative'
        elif digit == 1:
            return 'neutral'
        elif digit == 2:
            return 'positive'

    def get_user_sentiment(self, comment, a, b):
        print(f"Comment: {comment} \n")
        print("Sentiments: fury, usyk: ", a," ", b,"\n")
        user_sentiment_fury = input("Sentiment for Fury: ")
        user_sentiment_usyk = input("Sentiment for Usyk: ")

        return self.convert_digit_to_sentiment(user_sentiment_fury), self.convert_digit_to_sentiment(user_sentiment_usyk)

    def human_annotate(self, comments):
        comments = pd.DataFrame(comments).reset_index()

        sentiments_obj = []
        # Loop through the comments DataFrame.
        for i,comment in comments.iterrows():
            # Check if the comment has already been annotated
            if self.check_existing_annotations([comment.to_dict()]):
                continue
            # Get the user's sentiment for the comment
            user_sentiment_fury, user_sentiment_usyk = self.get_user_sentiment(comment['comment'], comment['fury_sentiment'], comment['usyk_sentiment'])
            # Write the annotation to the file
            sentiments_obj.append({
                'index': comment['index'],
                'comment': comment['comment'],
                'usyk_sentiment': user_sentiment_usyk,
                'fury_sentiment': user_sentiment_fury
            })
        # Check if there are any more comments to annotate
        if len(sentiments_obj) > 0:
            # Save the annotations to the file
            self.save_human_annotations(sentiments_obj)


    def calculate_accuracy(self, comments):
        accuracies = []
        annotations =  self.load_data_source(self.annotations_source)
        comments = pd.DataFrame(comments).reset_index()
        for i,comment in comments.iterrows():
            user_sentiment_fury = annotations[annotations['index'] == comment['index']]['fury_sentiment'].tolist()[0]
            user_sentiment_usyk = annotations[annotations['index'] == comment['index']]['usyk_sentiment'].tolist()[0]
            accuracy = (comment['fury_sentiment'] == user_sentiment_fury) and (
                        comment['usyk_sentiment'] == user_sentiment_usyk)
            if accuracy == False:
                print(f"Comment: {comment['comment']}")
                print(f"OpenAi sentiments: {comment['fury_sentiment']}, {comment['usyk_sentiment']}")
                print(f"User sentiments: {user_sentiment_fury}, {user_sentiment_usyk}")
            accuracies.append(accuracy)
        overall_accuracy = sum(accuracies) / len(accuracies)
        print(f"Batch {self.batch_end} Accuracy: {overall_accuracy}")
        return overall_accuracy

    def add_new_prompt(self):
        """
        Load the prompts from prompts.csv.
        Get the last prompt_id.
        Get the last prompt.
        Print the last prompt to the user.
        Get the new prompt from the user.
        Save the new prompt to prompts.csv.
        :return: prompt_id
        """
        prompts = self.load_data_source(self.prompt_source)
        prompt = prompts[prompts['prompt_id'] == self.prompt_id]['prompt'].tolist()[0]
        print(f"Last prompt: {prompt}")
        prompt = input("Enter new prompt: ")
        prompt = prompt.strip()
        if len(prompt) < 10:
            return self.prompt_id
        self.prompt_id += 1
        df = pd.DataFrame([{'prompt_id': self.prompt_id, 'prompt': prompt}])
        df.to_csv(self.prompt_source, mode='a', index=False, header=False)
        return self.prompt_id


    def update_comment_batches(self):
        """
        Update the batch start and end indices.
        Print the current batch start and end batch indices.
        Get user input for the batch start and end indices.
        :return:
        """
        print(f"Current batch start: {self.batch_start}")
        print(f"Current batch end: {self.batch_end}")
        self.batch_start = int(input("Enter new batch start: "))
        self.batch_end = int(input("Enter new batch end: "))

    def save_accuracy_score(self, accuracy):
        accuracy_obj = {
            'batch': self.batch_end,
            'prompt_id': self.prompt_id,
            'accuracy': accuracy
        }
        df = pd.DataFrame([accuracy_obj])
        # Append the results to the existing file
        print(df)
        df.to_csv(self.accuracy_source, mode='a', header=False, index=False)

    # check accraucy of prompt_id
    def check_accuracy(self, prompt_id):
        accuracy = self.load_data_source(self.accuracy_source)
        accuracy = accuracy[accuracy['prompt_id'] == prompt_id]['accuracy'].tolist()
        return accuracy[0]

    def save_human_annotations(self,sentiments_obj):
        df = pd.DataFrame(sentiments_obj)
        # Append the results to the existing file
        df.to_csv(self.annotations_source, index=False, mode='a', header=False)
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
        # write new line when the progress is 100%
        if progress == 1:
            sys.stdout.write('\n')
        sys.stdout.flush()  # Flush the output buffer
