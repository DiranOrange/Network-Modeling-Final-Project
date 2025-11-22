import os
import pandas as pd
import requests
import re

results_folder = "seed_paths"

def get_first_link(url):
    # Very useful
    base = 'https://www.britannica.com/'

    # Follow the link
    response = requests.get(url).text
    
    # First, get the topic in human readable terms
    try:
        topic = re.search("(?<=<title>).*(?=</title>)", 
                       response).group().split("|")[0].rstrip(" ")
    except AttributeError as e:
        print(url)
        print("problem child")

    # Some "articles" are actually pages which have many options for more articles to read
    # Since these are rare, manually handle them

    edge_cases = {
        "https://www.britannica.com/science/law-science": "https://www.britannica.com/topic/philosophy-of-science/Explanations-laws-and-theories",
        "https://www.britannica.com/topic/history-of-India":"https://www.britannica.com/place/India/History",
        "https://www.britannica.com/science/nature": "https://www.britannica.com/science/biophilia-hypothesis",
    }

    if url in edge_cases:
        return [topic, edge_cases[url]]

    # Different pages of britannica use different HTML styles
    start_string = {
        "money": "HTMLContent_HTMLContent__cOyPs"
        }
    
    # Determine page type (what comes after the base url)
    page_type = url[len(base):url.index("/", len(base))]

    # Now, look for the first link at the beginning of the article
    article_beginning = response.split(start_string.get(page_type, "<!--[BEFORE-ARTICLE]-->"))[1]
    
    # Drop clarifications in parantheses using a regex
    remaining_article = re.sub("[\(\[].*?[\)\]]", "", article_beginning)
    
    # Check the next link over and over until a valid one is found
    while True:
        first_url_index = remaining_article.index('<a href=')
        
        first_url = remaining_article[first_url_index:]
        
        link_start = first_url.index('"') + 1
        link_end = first_url.index('"', link_start)

        link = first_url[link_start:link_end]

        # If a link doesn't begin with www, HTML standards assume the link actually begins with the website's base link. Insert this        
        if base not in link:
            link = base[:-1] + link

        potential_problems = {
            "goes_to_dictionary": f"{base}dictionary" in link,
            "is_an_image": ".jpg" in link,
            "self_referential": "#ref" in link
        }

        # Don't use the link if it has a problem
        if any(potential_problems.values()):
            remaining_article = remaining_article[link_end:]
            continue
        
        return [topic, link]


if __name__ == "__main__":
    seed_links = list(pd.read_csv("seed_nodes.csv")["Britannica"])

    # Save what each link's topic is
    link_to_topic = {}
    
    # Assume: this is not the first time this script is run
    # Read the saved progress in the results folder
    grown_seeds = [os.path.join(results_folder, file)
                   for _, _, files in os.walk(results_folder)
                   for file in files]
    
    known_links = set(seed_links)

    # Add all the links already found to the known links
    for g in grown_seeds:
        G = pd.read_csv(g)
        known_links = known_links.union(set(G["Next Link"]))
        seed_links.remove(G["Current Link"][0])


    for link in seed_links:
        current_link_list, next_link_list = ([] for i in range(2))
       
        # i and seed used to monitor progress 
        i = 0
        seed = link
        current_link = link
        current_link_list.append(current_link)
        
        while True:
            i += 1
            current_topic, next_link = get_first_link(current_link)
            
            link_to_topic[current_link] = current_topic 
            
            next_link_list.append(next_link) 
            
            if next_link in known_links:
                break

            current_link = next_link
            current_link_list.append(current_link)
            known_links.add(current_link)

        print(f"{link_to_topic[s]}: {i}")


        # When constructing the network, we want to know topics, not links           # Not sure why, but sometimes a link doesn't have its topic saved 
        current_topic_list, next_topic_list = (list(map(lambda x: link_to_topic.get(x, get_first_link(x)[0]), links) # Fetch it by visiting the link
                                               for links in [current_link_list, next_link_list]))
        
        # Write the links and topics for this seed to an external CSV to save progress 
        pd.DataFrame({"Current Topic": current_topic_list,
                      "Current Link": current_link_list,
                      "Next Link": next_link_list,
                      "Next Topic": next_topic_list
                     }).to_csv(os.path.join(results_folder,f"{link_to_topic[s]}.csv"), index=False)

        # Aggregating the files together is trivial


