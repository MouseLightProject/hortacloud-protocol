from sc.fiji.snt.io import MouseLightLoader, MouseLightQuerier
from sc.fiji.snt.analysis import GroupedTreeStatistics, SNTChart
from sc.fiji.snt.annotation import AllenCompartment, AllenUtils
import random

# To run this script:
# 1. Download Fiji
# 2. Subscribe to the Neuronanatomy update site
# 3. Run it from within Fiji's script editor (File>New>Script...) & choose Python as language
#  Resources: 
#     Documentation: https://imagej.net/plugins/snt/
#     API:           https//javadoc.scijava.org/SNT/


def get_box_plot(arbor_type, metric):
    area_labels = ['CTX', 'HY', 'HPF'] # cortex, hypothalamus hippocampal formation
    dict = {}
    for label in area_labels:
        # Get all neuron IDs associated with this brain area
        compartment = AllenUtils.getCompartment(label)
        all_ids = MouseLightQuerier.getIDs(compartment)
        # For simplicity, do not retrieve more than 100 neurons
        n = min(len(all_ids), 100)
        sampled_ids = random.sample(all_ids, n)
        trees = []
        for id in sampled_ids:
            # Retrieve the actual reconstruction and add it to the lis
            trees.append(MouseLightLoader(id).getTree(arbor_type))
        dict[label] = trees
        
    # Assemble a GroupedTreeStatistics to established comparisons
    group_stats = GroupedTreeStatistics()
    for label, trees in dict.items():
        # Ad comparison group
        group_stats.addGroup(trees, label)

    return group_stats.getBoxPlot(metric)


if MouseLightQuerier.isDatabaseAvailable():
    # This is probably not very efficiency, as we'll be querying the
    # database multiple times to retrieve the same data, but given
    # the limited no. of cells it should only take a while to render
    # all the plot
    plot1 = get_box_plot('axon', 'Cable length')
    plot1.setChartTitle("Axons")
    plot2 = get_box_plot('dendrite', 'Cable length')
    plot2.setChartTitle("Dendrites")
    SNTChart.combine([plot1, plot2], True).show()
else:
    print("Aborting: Can only proceed with successful connection to database")
