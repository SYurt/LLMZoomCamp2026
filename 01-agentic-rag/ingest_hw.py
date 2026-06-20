from gitsource import GithubRepositoryDataReader
from minsearch import Index

def load_lesson_docs(repo_owner, repo_name, commit_id, allowed_extensions={"md"}, **kwargs):
    reader = GithubRepositoryDataReader(
        repo_owner=repo_owner,
        repo_name=repo_name,
        commit_id=commit_id,
        allowed_extensions=allowed_extensions,
        **kwargs
    )

    files = reader.read()

    documents = []
    for file in files:
        doc = file.parse()
        documents.append(doc)

    return documents

def build_index(documents):
    index = Index(
        text_fields=['content'],
        keyword_fields=['filename']
    )
    index.fit(documents)
    return index
