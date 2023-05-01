import openai


class TextMatching:
    def __init__(self, api_key, user_text, topic):
        self.api_key = api_key
        self.user_text = user_text
        self.topic = topic

    def matching(self):
        apikey = self.api_key
        openai.api_key = apikey
        promt = f"Соответствует ли данный текст: {self.user_text}. Теме: {self.topic}. Ответь да или нет."

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=promt,
            temperature=0.9,
            max_tokens=7,
            top_p=1,
            frequency_penalty=0.0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )

        return response.choices[0].text
