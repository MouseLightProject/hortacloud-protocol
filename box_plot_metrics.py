from sc.fiji.snt.io import MouseLightLoader, MouseLightQuerier
from sc.fiji.snt.analysis import GroupedTreeStatistics, MultiTreeStatistics, SNTChart
from sc.fiji.snt.annotation import AllenCompartment, AllenUtils


# To run this script:
# 1. Download Fiji
# 2. Subscribe to the Neuronanatomy update site
# 3. Run it from within Fiji's script editor (File->New->Script...), by choosing
#    Python as the scripting language
#  Resources:
#     Documentation:....https://imagej.net/plugins/snt/
#     API:..............https//javadoc.scijava.org/SNT/


def get_cells(area_labels):
    dict = {}
    histograms = []
    for label in area_labels:
        # Get all neuron IDs associated with this brain area
        compartment = AllenUtils.getCompartment(label)
        all_ids = MouseLightQuerier.getIDs(compartment)
        axons = []
        dendrites = []
        for id in all_ids:
            # Retrieve reconstructions. Add them to holding dictionary
            try:
                loader = MouseLightLoader(id)
                print("Retrieving cell {}...".format(id))
                axons.append(loader.getTree("axon"))
                dendrites.append(loader.getTree("dendrite"))
            except:
                print(".... Failure. Skipping cell...")
            finally:
                dict[label] = (axons, dendrites)
    return dict


def get_histograms(dict, metric, arbor_type="axon"):
    index = 0 if arbor_type == "axon" else 1
    histograms = []
    for (label, axon_dendrites) in dict.items():
        # For each group, assemble a MultiTreeStatistics instance to retrieve
        # frequencies and respective histogram
        stats = MultiTreeStatistics(axon_dendrites[index])
        hist = stats.getHistogram(metric)
        hist.setChartTitle(label)
        histograms.append(hist)
    return histograms


def get_box_plot(dict, metric, arbor_type="axon"):
    index = 0 if arbor_type == "axon" else 1
    # Assemble a GroupedTreeStatistics to established comparisons
    group_stats = GroupedTreeStatistics()
    for (label, axon_dendrites) in dict.items():
        # Ad comparison group
        group_stats.addGroup(axon_dendrites[index], label)
    return group_stats.getBoxPlot(metric)


def main(area_labels, metrics):
    cells_dict = get_cells(area_labels)

    for (label, axon_dendrites) in cells_dict.items():
        print("{}: Axons N={}; Dendrites N={}".format(
                label, len(axon_dendrites[0]), len(axon_dendrites[1])))

    for subarbor in ["axon", "dendrites"]:
        for metric in metrics:
            # Get histograms
            histograms = get_histograms(cells_dict, metric, subarbor)
            comb_hist = SNTChart.combine(histograms, 1, len(area_labels), True)
            comb_hist.setTitle(subarbor)
            comb_hist.show()
            # Get box plots
            boxplot = get_box_plot(cells_dict, metric, subarbor)
            boxplot.setTitle(subarbor)
            boxplot.show()


if MouseLightQuerier.isDatabaseAvailable():
    area_labels = ["CTX", "HY", "HPF"]  # cortex, hypothalamus, hippocampal formation
    metrics = ["Cable length", "Inter-node distance"]
    # This may take a while, depending on the no. of cells involved.
    # NB: Both metrics and brain areas acronyms are case sensitive
    main(area_labels, metrics)
else:
    print("Aborting: Can only proceed with successful connection to database")
