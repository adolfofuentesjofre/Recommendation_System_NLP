from apify_client import ApifyClient
import pandas as pd

places = pd.read_excel('C:/Users/cmurua/Documents/Repositorios Enjoy/Reviews/Categorias_Chiloe.xlsx')

# Selecciono los links de google de los lugares

google_link = places['location_link']
# Descarga de comentarios
with pd.ExcelWriter("reviews_v2.xlsx",engine='xlsxwriter') as writer:
    for i in range(len(places)):
        i=i+521
        print(i)
        place= places['location_link'].iloc[i]
        name = places['name'].iloc[i]
        # Initialize the ApifyClient with your API token
        client = ApifyClient("apify_api_woksBcyf1sS2yCXxFIUKYexPZJEjcW0uryMF")

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

        reviews.to_excel(writer, sheet_name=name[0:25]+'_'+str(i), index=False)




