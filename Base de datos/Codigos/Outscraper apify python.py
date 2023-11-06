from apify_client import ApifyClient
from outscraper import ApiClient
import pandas as pd



client = ApiClient(api_key='Z29vZ2xlLW9hdXRoMnwxMDQ1NzU4OTI2ODQ5NzgxNzU4NTN8ZDE2ZDM0ZTk1Yw')

# Search for businesses in specific locations:
place = 'church'
ciudad = ['Ancud','Las Animas']
Region = 'Los Lagos'
pais = 'Chile'
query = [place +', '+ciudad[0]+', '+Region+', '+pais,place +', '+ciudad[1]+', '+Region+', '+pais]
results = client.google_maps_search(query, limit=200, language='en')
places = pd.DataFrame(results[0])

# Se ordenan por cantidad de comentarios
places = places.sort_values('reviews',ascending=False)

# Se guarda la informacion de los lugares
places.to_excel(place+'_'+ciudad[0]+'_'+ciudad[1]+'_'+Region+'_'+pais+'.xlsx')


print(results)
# Selecciono los 5 lugares con mas comentarios.
top5_places = places.iloc[0:5]
google_link = top5_places['location_link']

# Descarga de comentarios
with pd.ExcelWriter("reviews.xlsx") as writer:
    for i in range(len(top5_places)):
        place= top5_places['location_link'].iloc[i]
        name = top5_places['name'].iloc[i]
        # Initialize the ApifyClient with your API token
        client = ApifyClient("apify_api_txoYFAnjzI3tMz56vd1xPGSw0VYDKP2uuWZ2")

        # Prepare the actor input
        run_input = {
            "startUrls": [{ "url": place }],
            "maxReviews": 20000,
            "language": "en",
        }

        # Run the actor and wait for it to finish
        run = client.actor("compass/Google-Maps-Reviews-Scraper").call(run_input=run_input)

        # Fetch and print actor results from the run's dataset (if there are any)
        reviews = pd.DataFrame()
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            reviews = reviews.append(item,ignore_index=True)

        reviews.to_excel(writer, sheet_name=name, index=False)




