import json
import copy
from matplotlib import pyplot
import reverse_geocoder
import numpy as np

properties = {'ciborium': {True: 'green', False: 'red'}, 
              'century': {'3rd': 'pink', '4th': 'teal', '5th': 'orange', '6th': "violet"}, 
              'depth_under_meter': {True: 'green', False: 'red'}, 
              'depth_step': {'10-35 cm': 'orange', '36-55 cm': 'yellow', '56-75 cm': 'green', '76-95 cm': 'teal', '96-115 cm': 'violet', '116-135 cm': 'pink', '136-160 cm': 'red'},
              'piscina_shape': {'other': 'perriwinkle', 'three-quarter round': 'royalblue', 'heptagon': 'magenta', 'rectangle': 'orange', 'polygon': 'blue', 'oval': 'violet', 'semicircle': 'green', 'round': 'yellow', 'square': 'teal', 'quatrefoil': 'purple', 'cross': 'pink', 'octogon': 'red', 'trapezoid': 'maroon', 'hexagon': 'gray', 'dekagon': 'brown', 'dodecagon': 'lightblue', 'trefoil': 'tan', 'horseshoe':'yellowgreen'}, 
              'shape': {'rectangle': 'orange', 'polygon': 'blue', 'semicircle': 'green', 'round': 'yellow', 'square': 'teal', 'quatrefoil': 'purple', 'cross': 'pink', 'octogon': 'red', 'trapezoid': 'maroon', 'hexagon': 'gray', 'central building': 'brown', 'inside a church': 'lightblue', 'trefoil': 'tan', 'irregular': 'redorange'},
              'region': {'Western Europe': 'purple', 'Eastern Europe': 'red', 'Southern Europe': 'green', 'Caucasus': 'gray', 'Middle East': 'orange', 'North Africa': 'blue', 'British Isles':'pink'}}


def read_data(file_name):
    # open data file and read it in
    with open(file_name, "r") as f:
        all_data = json.load(f)
        # make a copy of the data to change, while enumerating over the original
        data = copy.deepcopy(all_data['features'])
    # remove any baptisteries not certainly dated fifth century or earlier
    for item in all_data['features']:
        if item['properties']['date_before'] >= 600 or item['properties']['date_before'] == False:
            data.remove(item)
    # re-format to make data manipulation easier
    for idx, item in enumerate(data):
        item['properties']['coordinates'] = tuple(item['geometry']['coordinates'])
        data[idx] = item['properties']
        data[idx]['region'] = getplace(*data[idx]['coordinates'])
        del data[idx]['localisation_certainty'], data[idx]['id']
        if data[idx]['date'] < 300:
            data[idx]['century'] = "3rd"
        elif data[idx]['date'] < 400:
            data[idx]['century'] = "4th"
        elif data[idx]['date'] < 500:
            data[idx]['century'] = "5th"
        else: 
            data[idx]['century'] = "6th"
        if data[idx]['piscina_depth'] == False:
            data[idx]['depth_step'] = None
        elif data[idx]['piscina_depth'] <= 35:
            data[idx]['depth_step'] = '10-35 cm'
        elif data[idx]['piscina_depth'] <= 55:
            data[idx]['depth_step'] = '36-55 cm'
        elif data[idx]['piscina_depth'] <= 75:
            data[idx]['depth_step'] = '56-75 cm'
        elif data[idx]['piscina_depth'] <= 95:
            data[idx]['depth_step'] = '76-95 cm'
        elif data[idx]['piscina_depth'] <= 115:
            data[idx]['depth_step'] = '96-115 cm'
        elif data[idx]['piscina_depth'] <= 135:
            data[idx]['depth_step'] = '116-135 cm'
        else:
            data[idx]['depth_step'] = '136-160 cm'
        if data[idx]['piscina_shape'] == "" or data[idx]['piscina_shape'] == "unknown":
            data[idx]['piscina_shape'] = None
        if data[idx]['shape'] == "" or data[idx]['shape'] == "unknown":
            data[idx]['shape'] = None
        data[idx]['all'] = True

    return sorted(data, key=lambda x: x['date'])

def getplace(lon, lat):
    country_regions = {'EG':'Middle East', 
                       'DZ':'North Africa', 
                       'AM':'Caucasus', 
                       'BA':'Eastern Europe', 
                       'BG':'Eastern Europe', 
                       'RO':'Eastern Europe', 
                       'FR':'Western Europe', 
                       'GE':'Caucasus', 
                       'GR':'Southern Europe', 
                       'IL':'Middle East', 
                       'PS':'Middle East', 
                       'SY':'Middle East', 
                       'IT':'Southern Europe', 
                       'JO':'Middle East', 
                       'RS':'Eastern Europe', 
                       'HR':'Eastern Europe', 
                       'LB':'Middle East', 
                       'LY':'North Africa', 
                       'LI':'Western Europe', 
                       'MK':'Eastern Europe', 
                       'AT':'Western Europe', 
                       'CH':'Western Europe', 
                       'SI':'Eastern Europe', 
                       'ES':'Southern Europe', 
                       'TR':'Middle East', 
                       'TN':'North Africa', 
                       'CY':'Southern Europe',
                       'ET':'North Africa',
                       'AL':'Eastern Europe',
                       'DE':'Western Europe',
                       'GB':'British Isles',
                       'ER':'North Africa',
                       'IQ':'Middle East',
                       'ME':'Eastern Europe',
                       'PT':'Southern Europe',
                       'UA':'Eastern Europe'}
    return country_regions[reverse_geocoder.search((lat, lon),mode=1)[0]['cc']]

def count(data, _property):
    property_count = {item[_property]: 0 for item in data if item[_property] != None}
    for item in data:
        if item[_property] != None:
            property_count[item[_property]] += 1
    return property_count

def generate_pie_charts(data, pie_property, slice_property):
    fig, ax = pyplot.subplots(nrows=1, ncols=len((dict.fromkeys(item[pie_property] for item in data))))
    #fig.suptitle(slice_property + " by " + pie_property)
    for idx, option in enumerate(sorted(list(dict.fromkeys(item[pie_property] for item in data)))):
        subset = [item for item in data if item[pie_property] == option]
        #ax.set_title(str(option))
        property_count = count(subset, slice_property).items()
        print(property_count)
        for option in property_count.items():
            if option[1] == 1 and option[0] != 'other':
                property_count['other'] += 1
        ax[idx].pie([value for key,value in sorted(count(subset, slice_property).items(), key=lambda x: x[1]) if key == 'other' or value != 1], labels=[key for key,value in sorted(count(subset, slice_property).items(), key=lambda x: x[1]) if key == 'other' or value != 1], autopct=lambda p: '{:.0f}'.format(p * sum(count(subset, slice_property).values()) / 100), colors=[properties[slice_property][key] for key,_ in sorted(count(subset, slice_property).items(), key=lambda x: x[1])])
    pyplot.show()

def generate_pie_charts2(data, pie_property, slice_property):
    fig, ax = pyplot.subplots(nrows=2, ncols=2)
    #fig.suptitle(slice_property + " by " + pie_property)
    options = sorted(list(dict.fromkeys(item[pie_property] for item in data)))
    for idx in range(len(options)):
        subset = [item for item in data if item[pie_property] == options[idx]]
        ax[int(idx/2)][idx%2].set_title(str(options[idx]))
        ax[int(idx/2)][idx%2].pie([value for key,value in sorted(count(subset, slice_property).items(), key=lambda x: x[1])], labels=[key for key,value in sorted(count(subset, slice_property).items(), key=lambda x: x[1])], autopct=lambda p: '{:.0f}'.format(p * sum(count(subset, slice_property).values()) / 100), colors=[properties[slice_property][key] for key,_ in sorted(count(subset, slice_property).items(), key=lambda x: x[1])])
    # ax[2][1].axis("off")
    # ax[2][2].axis("off")
    pyplot.show()

def year_vs_region(data):
    z = {getplace(*item['coordinates']): {year: 0 for year in range(min([x['date_after'] for x in data]), max([x['date_before'] for x in data]) + 1)} for item in data}
    for item in data:
        for year in range(item['date_after'], item['date_before'] + 1):
            z[getplace(*item['coordinates'])][year] += 1

    fig, ax = pyplot.subplots()
    for region, years in z.items():
        ax.plot(years.keys(), years.values(), label=region, color=properties['region'][region])

    ax.set_xlabel('Year Created (A.D.)')
    ax.set_ylabel('Number of Baptisteries Created')
    ax.set_title('Baptisteries Created by Year and Region')
    ax.legend()

    pyplot.show()

    fig, ax = pyplot.subplots(4)

    regions = {getplace(*item['coordinates']): 0 for item in data}
    for item in data:
        regions[getplace(*item['coordinates'])] += 1
    ax[0].pie(regions.values(), labels=regions.keys())
    ax[0].set_title("By Region")

    century = {"3rd":0, "4th":0, "5th":0}
    for item in data:
        if item['date'] < 300:
            century["3rd"] += 1
        elif item['date'] < 400:
            century["4th"] += 1
        else:
            century["5th"] += 1
    ax[1].pie(century.values(), labels=century.keys())
    ax[1].set_title("By Century")

    piscina_shapes = {item['piscina_shape']: 0 for item in data}
    for item in data:
        piscina_shapes[item['piscina_shape']] += 1
    ax[2].pie(piscina_shapes.values(), labels=piscina_shapes.keys())
    ax[2].set_title("By Piscina Shape")

    shapes = {item['shape']: 0 for item in data}
    for item in data:
        shapes[item['shape']] += 1
    ax[3].pie(shapes.values(), labels=shapes.keys())
    ax[3].set_title("By Building Shape")
    
    fig.tight_layout()
    fig.suptitle("Baptisteries from 200 AD to 500 AD")
    pyplot.show()

def main():
    data = read_data("source.json")
   
    generate_pie_charts2(data, 'century', 'depth_step')


if __name__ == "__main__":
    main()