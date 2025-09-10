class FcmDto:
    def __init__(self,token_id : str, title : str, content : str):
        self.token_id = token_id
        self.title = title
        self.content = content
    def __str__(self):
        return f'token_id = {self.token_id}, title : {self.title}, content : {self.content}'
