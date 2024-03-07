import pandas as pd

class FeatureEngineering:

    def engagement(self, df, feature1, freature2):
        df['engagement'] = df[feature1] + (1 * df[freature2]) + 1
        return df

    def quantile_threshold(self, df, feature, threshold):
        threshold_feature = df[feature].quantile(threshold)
        filtered_feature = df[df[feature] > threshold_feature]
        return filtered_feature

    def categorize_comments(self, filtered_youtube_data):
        results = {
            'index': [],
            'category': []
        }

        usyk_keywords = ['usyk', 'oleksandr', 'ukrainian', 'osyk']
        fury_keywords = ['fury', 'tyson', 'gypsy', 'belly', 'king']

        filtered_youtube_data = filtered_youtube_data.reset_index()

        for i, data in filtered_youtube_data.iterrows():
            comment = data['clean_comment']
            index = data['index']

            results['index'].append(index)

            if any(keyword in comment for keyword in usyk_keywords) and not any(
                    keyword in comment for keyword in fury_keywords):
                results['category'].append('usyk')

            elif any(keyword in comment for keyword in fury_keywords) and not any(
                    keyword in comment for keyword in usyk_keywords):
                results['category'].append('fury')

            elif any(keyword in comment for keyword in fury_keywords) and any(
                    keyword in comment for keyword in usyk_keywords):
                results['category'].append('fury_usyk')

            else:
                results['category'].append('none')

        categorized_comments = pd.DataFrame(results)
        merge_data = pd.merge(filtered_youtube_data, categorized_comments, on='index', how='inner')

        # Set the index back to the original one
        merge_data.set_index('index', inplace=True, drop=True)

        return merge_data

    def transform_to_ternary(self, usyk_sentiment, fury_sentiment):
        if usyk_sentiment == 'positive' and fury_sentiment != 'positive':
            return 'favoring_usyk'
        elif fury_sentiment == 'positive' and usyk_sentiment != 'positive':
            return 'favoring_fury'
        else:
            return 'neutral'