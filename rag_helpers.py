from abc import ABC, abstractmethod
from dataclasses import dataclass



INSTRUCTIONS = '''
Your task is to answer questions from the course participants
based on the provided context.

Use the context to find relevant information and provide accurate
answers. If the answer is not found in the context,
respond with "I don't know."
'''

PROMPT_TEMPLATE = '''
QUESTION: {question}

CONTEXT:
{context}
'''.strip()


@dataclass
class Output:
    output_text: str
    input_tokens: int = 0
    output_tokens: int = 0

class RAGBase:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        model='gpt-5.4-mini'
    ):
        self.index = index
        self.llm_client = llm_client
        self.instructions = instructions
        self.prompt_template = prompt_template
        self.model = model

    @abstractmethod
    def search(self, query, num_results=5):
       pass

    @abstractmethod
    def build_context(self, search_results):
        pass

    def build_prompt(self, query, search_results):
        context = self.build_context(search_results)
        return self.prompt_template.format(
            question=query, context=context
        )

    def llm(self, prompt):
        input_messages = [
            {'role': 'developer', 'content': self.instructions},
            {'role': 'user', 'content': prompt}
        ]

        response = self.llm_client.responses.create(
            model=self.model,
            input=input_messages
        )

        return response

    def rag(self, query):
        search_results = self.search(query)
        prompt = self.build_prompt(query, search_results)
        response = self.llm(prompt)
        output = Output(
            response.output_text,
            response.usage.input_tokens,
            response.usage.output_tokens
            )
        return output


class RAGFAQ:

    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        course='llm-zoomcamp',
        model='gpt-5.4-mini'
    ):
        super().__init__(
            index,
            llm_client,
            instructions=instructions,
            prompt_template=prompt_template,
            model=model
    )

        self.course = course

    def search(self, query: str, num_results: int = 5) -> dict[str, str]:
        """
        Search the FAQ database for entries matching the given query.
        """
        boost_dict = {'question': 3.0, 'section': 0.5}
        filter_dict = {'course': self.course}

        return self.index.search(
            query,
            num_results=num_results,
            boost_dict=boost_dict,
            filter_dict=filter_dict
        )

    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc['section'])
            lines.append('Q: ' + doc['question'])
            lines.append('A: ' + doc['answer'])
            lines.append('')

        return '\n'.join(lines).strip()

   
class RAGLlmZoomCamp(RAGBase):
    
    def __init__(
        self,
        index,
        llm_client,
        instructions=INSTRUCTIONS,
        prompt_template=PROMPT_TEMPLATE,
        model='gpt-5.4-mini'
    ):
        super().__init__(
            index,
            llm_client,
            instructions=instructions,
            prompt_template=prompt_template,
            model=model
        )

    def search(self, query: str, num_results: int=5) -> list[dict[str, str]]:
        """
        Search the LLM ZoomCamp lessons for entries matching the given query.
        """

        return self.index.search(
            query,
            num_results=num_results)
    
    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc['content'])
            lines.append('file: ' + doc['filename'])
            lines.append('')

        return '\n'.join(lines).strip()
    
    
      
class SearchLessons:
    def __init__(self, index):
        self.index = index
        
    def search(self, query: str, num_results: int=5) -> list[dict[str, str]]:
        """
        Search the LLM ZoomCamp lessons for entries matching the given query.
        """

        return self.index.search(
            query,
            num_results=num_results)
    
    def build_context(self, search_results):
        lines = []

        for doc in search_results:
            lines.append(doc['content'])
            lines.append('file: ' + doc['filename'])
            lines.append('')

        return '\n'.join(lines).strip()    