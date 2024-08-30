from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from ..models import BasketAnalysis

API_KEY="<API_KEY_HERE>"

# HELPER FUNCTION
def get_basket_analysis():
  basket_analysis = BasketAnalysis.objects.last() 
  input_basket_str = basket_analysis.basket_data

  return input_basket_str

# EXECUTION FUNCTION
def solve_user_query(query) :
  llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=1,
    max_tokens=None,
    timeout=None,
    api_key=API_KEY,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
  )
  prompt_template = PromptTemplate.from_template("We have Provided the CSV analyzed by sales using market basket analysis. It tells what items are most likely to be picked up by the users. I want you to memorize them and put common sense in it (to not pair toilet paper with apples, as that would be impossible). Questions will be asked to you regarding where should the mart employee place the product to get highest sales possible. The Arrays of items are provided to you in both consequents & antecedents column. \n The Data is : \n {data} \n The Query you have to process : {query}")

  input_basket = get_basket_analysis()
  prompt = prompt_template.invoke({"data" : input_basket, "query" : query})

  response = llm.invoke(prompt)

  return response.content

def give_imp_pairs() : 
  llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=1,
    max_tokens=None,
    timeout=None,
    api_key=API_KEY,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
  )

  prompt_template = PromptTemplate.from_template("We have provided the CSV analyzed by sales using market basket analysis, It tells what items are most likely to be bought or picked upby the consumers, I want you to read this data and give me a list of pairs that are important and must be kept near. You just have to provide the Highest, moderate, lowest priority list without much explanation. \n The Data is : \n {data}")

  input_basket = get_basket_analysis()
  prompt = prompt_template.invoke({"data" : input_basket})

  response = llm.invoke(prompt)

  return response.content