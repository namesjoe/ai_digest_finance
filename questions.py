questions = [
"Summarize the key findings  in all abstract parts of this articlesfrom the provided research articles. Please describe widely and citate most intersting.",
"What are the main themes or trends emerging from these articles? Take into account only abstracts (values)",
"Can you identify any commonalities or connections between the different research papers?",
"What are the major implications or future directions suggested by this research? Describe future possibilities.",
]

replace_items_prefix = [
    "**1.", "**2.", "**3.", "**4.", "**5.", "**6.", "**7.", "**8.", "**9."
]

replace_items_postfix = [
    "** ", ": "
]

def replacer(str_value: str, replace_items: list, prefix=True):
    if prefix:
        for ri in replace_items:
            str_value = str_value.replace(ri, f"\n{ri}")
    else:
        for ri in replace_items:
            str_value = str_value.replace(ri, f"{ri}\n")
    return str_value

