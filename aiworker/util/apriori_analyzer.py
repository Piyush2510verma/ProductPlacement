import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from ..models import BasketAnalysis

# HELPER FUNCTION

def convert_to_list(frozen_set_string):
  cleaned_string = frozen_set_string.replace("frozenset({", "").replace("})", "")
  item_list = [item.strip("'") for item in cleaned_string.split("', '")]
  return item_list


# EXPORT FUNCTIONS

def init_placement_ai(products_df, purchases_df) :
  purchases_df['PURCHASES'] = purchases_df['PURCHASES'].apply(eval)
  merged_data = purchases_df.explode('PURCHASES').merge(products_df, left_on='PURCHASES', right_on='SKU')
  
  basket = merged_data.groupby(['Name', 'PRODUCT_NAME']).size().unstack().reset_index().fillna(0).set_index('Name')

  basket = basket.applymap(lambda x: 1 if x > 0 else 0)

  frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)

  if frequent_itemsets.empty:
    raise Exception("No Frequent Itemset found with Min_support")
  else:
    frequent_itemsets = frequent_itemsets.sort_values(by='support', ascending=False)

    rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.8)
    rules = rules.sort_values(by='lift', ascending=False)

    merged_rules = (
        rules.groupby('consequents')
        .agg({
            'antecedents': lambda x: ', '.join([str(antecedent) for antecedent in x]),
            'support': 'mean',
            'confidence': 'mean',
            'lift': 'mean'
        })
        .reset_index()
    )

    with pd.ExcelWriter('basket_analysis.xlsx') as writer:
      frequent_itemsets.to_excel(writer, sheet_name='Frequent Itemsets', index=False)
      merged_rules.to_excel(writer, sheet_name='Merged Association Rules', index=False)
    
    parse_basket_analysis()


def parse_basket_analysis() :
  df = pd.read_excel("basket_analysis.xlsx", sheet_name="Merged Association Rules")

  df['consequents'] = df['consequents'].apply(convert_to_list)
  df['consequents'] = df['consequents'].apply(lambda x: ['"' + item + '"' for item in x])

  df['antecedents'] = df['antecedents'].apply(convert_to_list)
  df['antecedents'] = df['antecedents'].apply(lambda x: ['"' + item + '"' for item in x])

  input_basket_df = df.drop(columns=['support', 'confidence', 'lift'])

  input_basket_str = input_basket_df.to_csv(index=False)

  basket_analysis = BasketAnalysis.objects.first()

  if basket_analysis:
    basket_analysis.basket_data = input_basket_str
    basket_analysis.save()
  else:
    BasketAnalysis.objects.create(basket_data=input_basket_str)

