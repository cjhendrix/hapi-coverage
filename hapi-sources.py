import urllib.request
import json

def fetch_data(base_url, limit=1000):
    """
    Fetch data from the provided base_url with pagination support.

    Args:
    - base_url (str): The base URL endpoint to fetch data from.
    - limit (int): The number of records to fetch per request.

    Returns:
    - list: A list of fetched results.
    """

    idx = 0
    results = []

    while True:
        offset = idx * limit
        url = f"{base_url}&offset={offset}&limit={limit}"
        print(url)
        with urllib.request.urlopen(url) as response:
            print(f"Getting results {offset} to {offset+limit-1}")
            json_response = json.loads(response.read())

            results.extend(json_response['data'])

            # If the returned results are less than the limit, it's the last page
            if len(json_response['data']) < limit:
                break

        idx += 1

    return results

def make_markdown_table(array, align: str =None):
    """
    Args:
        array: The array to make into a table. Mush be a rectangular array
               (constant width and height).
        align: The alignment of the cells : 'left', 'center' or 'right'.
    """
    # make sure every elements are strings
    array = [[str(elt) for elt in line] for line in array]
    # get the width of each column
    widths = [max(len(line[i]) for line in array) for i in range(len(array[0]))]
    # make every width at least 3 colmuns, because the separator needs it
    widths = [max(w, 3) for w in widths]
    # center text according to the widths
    array = [[elt.center(w) for elt, w in zip(line, widths)] for line in array]

    # separate the header and the body
    array_head, *array_body = array

    header = '| ' + ' | '.join(array_head) + ' |'

    # alignment of the cells
    align = str(align).lower()  # make sure `align` is a lowercase string
    if align == 'none':
        # we are just setting the position of the : in the table.
        # here there are none
        border_left   =  '| '
        border_center = ' | '
        border_right  = ' |'
    elif align == 'center':
        border_left   =  '|:'
        border_center = ':|:'
        border_right  = ':|'
    elif align == 'left':
        border_left   =  '|:'
        border_center = ' |:'
        border_right  = ' |'
    elif align == 'right':
        border_left   =  '| '
        border_center = ':| '
        border_right  = ':|'
    else:
        raise ValueError("align must be 'left', 'right' or 'center'.")
    separator = border_left + border_center.join(['-'*w for w in widths]) + border_right

    # body of the table
    body = [''] * len(array)  # empty string list that we fill after
    for idx, line in enumerate(array[1:]):
        # for each line, change the body at the correct index
        body[idx] = '| ' + ' | '.join(line) + ' |'
    body = '\n'.join(body)

    return header + '\n' + separator + '\n' + body

def create_table_data(coverage,themes,countries):
    themes = sorted(themes)
    countries = sorted(countries)
    output = []
    output.append(['']+themes)
    for country in countries:
        row = [country]
        for theme in themes:
            cell = 'No'
            if theme in coverage:
                if country in coverage[theme]:
                    adm_coverage = coverage[theme][country]['coverage']
                    cell = f'Yes (adm{adm_coverage})'
            row.append(cell)
        output.append(row)
    return output



THEMES = ['3w','population','food_security','national_risk','humanitarian_needs']

BASE_URL = "https://stage.hapi-humdata-org.ahconu.org/api/themes/"
LIMIT = 10000

coverage = {}
all_countries = []

for theme in THEMES:
    print(f'Getting results for {theme}')
    coverage[theme] = {}
    theme_url = f"{BASE_URL}{theme}?output_format=json&app_identifier=Y292ZXJhZ2Vfc2NyaXB0OnNpbW9uLmpvaG5zb25AdW4ub3Jn"
    results = fetch_data(theme_url, LIMIT)
    countries = {}
    for row in results:
        if row['location_name'] not in countries:
            countries[row['location_name']] = []
        if row['location_name'] not in all_countries:
            all_countries.append(row['location_name'])
        if row['resource_hdx_id'] not in countries[row['location_name']]:
            countries[row['location_name']].append(row['resource_hdx_id'])

    coverage[theme] = countries

output = ''

for theme in coverage:
    theme_table = [['Country','Dataset','Source']]
    for country in coverage[theme]:
        data_source_str = ''
        data_provider = ''
        prev_resource = ''
        for index, resource in enumerate(coverage[theme][country]): 
            base_url = f'https://stage.hapi-humdata-org.ahconu.org/api/resource?hdx_id={resource}&update_date_min=2020-01-01&update_date_max=2024-12-31&output_format=json&app_identifier=Y292ZXJhZ2Vfc2NyaXB0OnNpbW9uLmpvaG5zb25AdW4ub3Jn'
            data = fetch_data(base_url, LIMIT)
            resource_data = data[0]
            if resource_data['dataset_title']!=prev_resource:
                prev_resource = resource_data['dataset_title']
                data_source_str = data_source_str + f" [{resource_data['dataset_title']}]({resource_data['hdx_link']})"
                
                data_provider = data_provider + f" {resource_data['dataset_hdx_provider_name']}"
        
        theme_table.append([country,data_source_str,data_provider])

    print(f'## {theme}')
    print(make_markdown_table(theme_table,'center'))

#table_data = create_table_data(coverage,THEMES,all_countries)
#print(table_data)
#print(make_markdown_table(table_data,'center'))
