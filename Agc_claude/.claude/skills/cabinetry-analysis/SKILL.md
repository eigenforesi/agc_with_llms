---
name: cabinetry-analysis
description: Guidance for implementing the statistical analysis component of an analysis in HEP, using cabinetry. Use to build configuration and fit model to data for a given analysis.
---

# Cabinetry Analysis

## Overview

This skill provides the necessary information to take an existing pipeline that produces histograms or ntuples and implement the statistical analysis using cabinetry.

## Core workflow

1. User decides on the high-level information (POI, regions, systematics, etc.).  This will be provided by the user in the prompt.
2. Build a .yml file with configuration information which cabinetry will use to create the workspace.
3. Use the `cabinetry` Python package to build the workspace and fit the model to data.
4. Create useful plots of the fit results such as pull plots, correlations, and post-fit distributions.

Below are explanations of the three core steps in more detail and how to implement them.

## Create configuration .yml file

Use the information given to you in the notebook Analysis.ipynb in order to create a .yml file representing the configuration of the statistical analysis.  
Put this new file in the sandbox, do not modify any other files, and name the file config.yml.  
Below is a brief summary of general guidelines you should follow, the syntax and exact structure you should follow for creating the .yml file, and the meanings of every entry in the config file.

General info:
See user prompt for this general info

Syntax to be followed:

General:
  Measurement: "<measurement_name>"
  POI: "<POI>"
  HistogramFolder: "<histogram_directory>"
  InputPath: "<hist_root_filename>.root:{SamplePath}{VariationPath}"
  VariationPath: ""

Regions:
  - Name: <Region_1>
  - Filter: <region_selection> [if more than one region]

[add more regions as necessary]

Samples:
  - Name: "Data"
    SamplePath: "<data_path>"
    Data: True

  - Name: "Signal"
    SamplePath: "<signal_path>"

  - Name: "Background <bkg_1_name>"
    SamplePath: "<bkg_1_path>"

[add more background processes as necessary]

Systematics:
  - Name: "<shape_syst_name>"
    Type: "NormPlusShape"
    Up:
      VariationPath: “<up_variation_suffix>"
    Down:
      VariationPath: “<down_variation_suffix>"

[more sources of systematic uncertainty affecting distribution shape]

  - Name: "<norm_syst_name>"
    Type: "Normalization"
    Up:
      Normalization: <up_shift>
    Down:
      Normalization: <down_shift>
    Samples: "<relevant_samples>"

[more sources of systematic uncertainty affecting only normalization]


NormFactors:
  - Name: <norm_factor_name>
    Samples: <nf_sample>
    Nominal: 1.0
    Bounds: [<nf_lbnd>, <nf_hbnd>]

[more NormFactors which scale specific samples without prior constraints]



Meanings of the parameters:
<measurement_name> = string, name of the measurement being done (Ex: CabinetryHZZAnalysis)
<POI> = parameter of interest, will be specified by the user for now
<histogram_directory> = directory where histograms are to be saved, and directory where histograms (or ntuples are to be read from) are taken from for input
<hist_root_filename> = root file where histograms or ntuples are to be taken from.
<Region_1> = name of Region 1 (example: signal region.  Other regions might be control region, validation region, etc.)
<region_selection> = criteria events must satisfy to be in this region (example: pT > 100).  This parameter is unnecessary if there is only one region.
<data_path> = path to histogram (the name of the histogram in the .root file) where data is stored (usually it is called just “data”.  Check the earlier code where the histograms were created.)
<signal_path> = path to histogram where MC simulated signal is stored (usually it is called just “signal”.  Check the earlier code where the histograms were created.)
<bkg_1_name> = name of background process 1 that is being modelled
<bkg_1_path> = path to histogram where MC simulated background process 1 is stored (usually it will be called the name of the particular background process we are considering, such as “ZZ” or “Z_tt”.  Check the earlier code where the histograms were created.)
<shape_syst_name> = unique name identifying the systematic uncertainty (e.g. JES, TauID, PDF). This label corresponds to a single nuisance parameter in the fit and should reflect the physical source of uncertainty.
<up_variation_suffix> = suffix appended to the nominal histogram path to access the +1σ (upward) variation of this systematic. It points to a histogram where the distribution has been recomputed under this shifted condition.
<down_variation_suffix> = suffix appended to access the −1σ (downward) variation histogram. Together with the up variation, this defines how the shape and normalization change as the nuisance parameter varies.
<norm_syst_name> = unique name for a normalization-only systematic (e.g. lumi, ZZ_norm). This defines a nuisance parameter that scales yields without altering histogram shapes.
<up_shift> = fractional change in yield for a +1σ shift (e.g. 0.1 means +10%). This defines how much the sample normalization increases when the nuisance parameter is +1.
<down_shift> = fractional change for a −1σ shift (e.g. -0.1 means −10%). Typically symmetric with the up shift, but not required to be.
<relevant_samples> = sample or list of samples affected by this systematic (e.g. "Background ZZ" or ["ttbar", "Wjets"]). This restricts where the nuisance parameter is applied in the model.
<norm_factor_name> = name of the normalization factor (e.g. mu_signal, ttbar_norm). This becomes a free parameter in the fit and may represent the parameter of interest (POI) or a floating background normalization.
<nf_sample> = sample (or list of samples) that this NormFactor scales. It defines which components of the model are multiplied by this parameter during the fit.
<nf_lbnd> = lower bound allowed for the NormFactor during the fit (e.g. 0). This constrains the physically allowed range of the parameter.
<nf_hbnd> = upper bound for the NormFactor (e.g. 10). This prevents unphysical or numerically unstable solutions during the likelihood maximization.



## Build workspace

The code given to you so far in the file Analysis.ipynb is an analysis pipeline, minus the statistical analysis.
You will now start implementing the statistical analysis with cabinetry, by creating a workspace.
First, check if cabinetry has been imported in the analysis file; if not, import it.
The easiest way to create a cabinetry workspace is to start with a configuration object.  This is imported from a .yml file created in the previous step.
A configuration object is initialized like 
```cabinetry.configuration.load("<path/to/config/file>")```
Print the ["Samples"] and ["Systematics"] elements of the config object.
Then apply the methods:
```cabinetry.templates.collect(<config_object>)```
```cabinetry.templates.postprocess(<config_object>)```
Then create a workspace object using 
```cabinetry.workspace.build(<config_object>)```
This workspace is what you will use to do the rest of the statistical analysis.



## Fit model to data and create plots

The code given to you so far in Analysis.ipynb is an anlysis pipeline that is written up until the creation of a statistical workspace.
This statistical workspace contains information on the model for our data, and the data itself.
You will now write code to take this workspace and actually perform the fit, generating output plots for the user to analyse the results.

Start a new cell in the Analysis.ipynb file and implement as follows:

Write the code snippet ```model, data = cabinetry.model_utils.model_and_data(<workspace>)```.  This creates model and data objects
The argument <workspace> is to be replaced by the name of the cabinetry workspace objects previously created.

Then perform the fit using ```fit_results = cabinetry.fit.fit(model, data)```.

Now we create plots showing the fit results:
There are multiple plots we might want to examine.

To make pull plot:  
```
cabinetry.visualize.pulls(
    fit_results, exclude="Signal_norm", close_figure=False, save_figure=False
)
utils.save_figure("pulls")
```

The above code creates both a .pdf and a .png file of the plot.
If we want only a .pdf, omit the last line beginning with `utils` and set save_figure to True in the cabinetry.visualize.pulls() line.
By default, save as both a .pdf and .png unless otherwise specified.

To make plot visualizing correlations between parameters:
```
cabinetry.visualize.correlation_matrix(
    fit_results, pruning_threshold=0.15, close_figure=False, save_figure=False
)
utils.save_figure("correlation_matrix")
```

Follow same changes as before in the case that we want only a .pdf plot.

Now we want to actually visualize our fit with the data.  Create a post-fit model using:
```postfit_model = cabinetry.model_utils.prediction(model, fit_results=fit_results)```

We now need to create an object called plot_config.
The plot_config object should be a python dictionary object where there is a key called "Regions".
The value for this key should be a list (syntax as [item1, item2, etc...]) where every element of the list is a dictionary.
In this dictionary, there should be a "Name" key with the value having the name of the region (from the config),
and a "Binning" key with the value having a list representing the binning (easiest to make this from a linspace).
Create the plot_config object first (for the signal region).
Then plot the data and fit in this region using (this will output a list of dictionaries each containing a figure and region name):

```
figure_dict = cabinetry.visualize.data_mc(
    postfit_model, data, config=plot_config, save_figure=False
)
```

For each figure, give it a meaningful x-axis label.  This can be done like so:

```
fig = figure_dict[i]["figure"]
fig.axes[1].set_xlabel("<title of quantity being plotted>")
```

i indexes the particular plot being made as listed in the figure_dict list.

Then save and export this figure like so:
```utils.save_figure("<Descriptive name for the post-fit plot in this region>")```


For each new plot being made, start a new cell for better organization.