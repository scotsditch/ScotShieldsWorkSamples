
# import libraries

import numpy as np
import pandas as pd
from time import time
import scipy.stats as stats

from IPython.display import display # Allows the use of display() for DataFrames

# # Pretty display for notebooks
# %matplotlib inline

###########################################
# Suppress matplotlib user warnings
# Necessary for newer version of matplotlib
import warnings
warnings.filterwarnings("ignore", category = UserWarning, module = "matplotlib")
#
# Display inline matplotlib plots with IPython
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
###########################################

import matplotlib.pyplot as plt
import matplotlib.cm as cm

import warnings
warnings.filterwarnings('ignore')

import seaborn as sns

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA








### HELPER FUNCTIONS:

# Initial Exploration



def exp1(df):

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        # shape of data

        print('rows and columns: {}'.format(df.shape))

        # head data

        # display(df.head())
        print('')
        # data types and columns in data
        print('data types and columns in data:')
        print('')
        #display(df.info())
        print(df.info())
        print('')
        # unique values in each column
        print('unique values in each column:')
        #display(df.nunique())
        print(df.nunique())
        print('')
        # percentage duplicates
        print('percentage duplicates : {}'.format(1-(float(df.drop_duplicates().shape[0]))/df.shape[0]))
        print('')
        ## Percentage of column with missing values
        print('Percentage of column with missing values:')
        print('')
        missingdf=df.apply(lambda x: float(sum(x.isnull()))/len(x))

        #display(missingdf.head(n=missingdf.shape[0]))
        print(missingdf.head(n=missingdf.shape[0]))
        print('')
        print('Data snapshot:')
        print('')

        print(df[:5])

# plot all continuous variables by all categorical variables
# get distributions

def plotter(ca_col,co_col,d_df,p_typ='boxplot'):

    if ca_col is None:
        for i in co_col:
            if p_typ=='boxplot':
                #d_df.boxplot(column=i)
                d_df[[i]].plot.box(subplots=True)
                plt.tight_layout()
            elif p_typ=='hist':
                d_df.hist(column=i)
            elif p_typ=='kde':
                #d_df[[i]].plot.kde()


                # Density Plot and Histogram of all arrival delays
                plt.figure()


                sns.distplot(d_df[i], hist=True, kde=True,
                             # Updated: 6/26/19 more than 50 bins runs too slow
                             bins=min(50,int(d_df.shape[0]/5)),
                             #bins=int(data_df.shape[0]/5),
                             color = 'darkblue',
                             hist_kws={'edgecolor':'black'},
                             kde_kws={'linewidth': 4})

                d_df[[i]].plot.box(subplots=True)
                plt.tight_layout()
                plt.show()


    elif ca_col!=None:
        for j in ca_col:
            for i in co_col:
                if p_typ=='boxplot':
                    d_df.boxplot(column=i,by=j)
                elif p_typ=='hist':
                    d_df.hist(column=i,by=j)
                elif p_typ=='kde':
                    #print('TODO')
                    #d_df[[i]].plot.kde()

                    plt.figure()

                    g = sns.FacetGrid(d_df, col=j, margin_titles=True)
                    g.map(sns.distplot,
                          i,
                          # Updated: 6/26/19 more than 50 bins runs too slow
                          bins=min(50,int(d_df.shape[0]/5)),
                          #bins=int(data_df.shape[0]/5),
                          color='darkblue',
                          hist_kws={'edgecolor': 'black'},
                          kde_kws={'linewidth': 4})

                    d_df.boxplot(column=i,by=j)
                    #d_df[[i]].plot.box(subplots=True)
                    plt.tight_layout()
                    plt.show()

# create list of dataframes of variables aggregated by cat variables

def agger(ca_col, i_col, d_df, agger):
    empt=[]
    for i in ca_col:
        for j in i_col:
            cont_df=d_df.copy()
            cont_df=cont_df.groupby(i).agg({j:agger})
            empt.append(cont_df)
    return empt




# plot counts of id variables by cat value

def id_plot(ca_col2, i_col2, d_df2):
    lst=agger(ca_col=ca_col2, i_col=i_col2, d_df=d_df2, agger='nunique')
    [i.plot(kind='bar') for i in lst]


# creates columns for all specified time periods

def ts_periods(f_nm, d_list, d_df):
    t_df=d_df.copy()

    for i in d_list:
        if i=='year':
            t_df[f_nm+'_year']=pd.DatetimeIndex(t_df[f_nm]).year
        elif i=='month':
            t_df[f_nm+'_month']=pd.DatetimeIndex(t_df[f_nm]).month
        elif i=='weekday':
            t_df[f_nm+'_weekday']=pd.DatetimeIndex(t_df[f_nm]).weekday_name
        elif i=='week' in d_list:
            t_df[f_nm+'_week']=pd.DatetimeIndex(t_df[f_nm]).week
        elif i=='hour':
            t_df[f_nm+'_hour']=pd.DatetimeIndex(t_df[f_nm]).hour
        elif i=='minute':
            t_df[f_nm+'_minute']=pd.DatetimeIndex(t_df[f_nm]).minute
    return t_df


# correlation between categorical variable and continuous variable

def CatConCor(df,catVar,conVar):
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

    # subsetting data for one categorical column and one continuous column
    data2=df.copy()[[catVar,conVar]]
    data2[catVar]=data2[catVar].astype('category')



    # updated 10/7/19

    argStr="Q('"+conVar+"') ~ Q('"+catVar+"')"

    mod = ols(argStr,data=data2).fit()




#     mod = ols(conVar+'~'+catVar,
#                 data=data2).fit()

    aov_table = sm.stats.anova_lm(mod, typ=2)

    if aov_table['PR(>F)'][0] < 0.05:
        print('Correlated p='+str(aov_table['PR(>F)'][0]))
    else:
        print('Uncorrelated p='+str(aov_table['PR(>F)'][0]))


### MinMax Scale data
# Note: need to change this to subset df by list_cont

def scaleData(s_df,list_cont):
    # Import sklearn.preprocessing.StandardScaler
    from sklearn.preprocessing import MinMaxScaler

    # Initialize a scaler, then apply it to the features
    scaler = MinMaxScaler()
    s_df[list_cont]=scaler.fit_transform(s_df[list_cont])

    return s_df



# minMax scale perform pca and run silhouette scores for clustering

def scalePcaCluster(spc_df,numList):
    scaledDf=scaleData(s_df=spc_df,list_cont=numList)

    # correlation
    display(scaledDf.corr())

    # segmenting with PCA

    from sklearn.decomposition import PCA

    pca_spc = PCA().fit(scaledDf)

    # plot isn't iterable for less than 5 columns
    if len(numList)>5:
        pca_results_spc = pca_results2(scaledDf, pca_spc)
    else:
        pca_results_spc = pca_results(scaledDf, pca_spc)

    # determining cluster number with silhouette score

    ## K-Means Clustering:

    emptDct={}

    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    # Loop through clusters
    for n_clusters in range(2,len(numList)):
        # TODO: Apply your clustering algorithm of choice to the reduced data
        clusterer = KMeans(n_clusters=n_clusters).fit(scaledDf)

        # TODO: Predict the cluster for each data point
        preds = clusterer.predict(scaledDf)

        # TODO: Find the cluster centers
        centers = clusterer.cluster_centers_

        # TODO: Predict the cluster for each transformed sample data point
        # sample_preds = clusterer.predict(pca_samples)

        # TODO: Calculate the mean silhouette coefficient for the number of clusters chosen
        score = silhouette_score(scaledDf, preds, metric='euclidean')
        print("For n_clusters = {}. The average silhouette_score is : {}".format(n_clusters, score))

        emptDct.update({n_clusters:score})


    # plotting silhouette scores
    from matplotlib.ticker import MaxNLocator
    ax = plt.figure().gca()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # updated 10/8/19
    plt.plot(list(emptDct.keys()),list(emptDct.values()))


 # create bar plots for fields in list

def plotbar(df,flist):
    for x in flist:
        display(df[[x]].plot(figsize=(20,5),kind='bar',rot=90))




# segmentation helper functions

def pca_results(good_data, pca):
	'''
	Create a DataFrame of the PCA results
	Includes dimension feature weights and explained variance
	Visualizes the PCA results
	'''

	# Dimension indexing
	dimensions = dimensions = ['Dimension {}'.format(i) for i in range(1,len(pca.components_)+1)]

	# PCA components
	components = pd.DataFrame(np.round(pca.components_, 4), columns = good_data.keys())
	components.index = dimensions

	# PCA explained variance
	ratios = pca.explained_variance_ratio_.reshape(len(pca.components_), 1)
	variance_ratios = pd.DataFrame(np.round(ratios, 4), columns = ['Explained Variance'])
	variance_ratios.index = dimensions

	# Create a bar plot visualization
	fig, ax = plt.subplots(figsize = (14,8))

	# Plot the feature weights as a function of the components
	components.plot(ax = ax, kind = 'bar');
	ax.set_ylabel("Feature Weights")
	ax.set_xticklabels(dimensions, rotation=0)


	# Display the explained variance ratios
	for i, ev in enumerate(pca.explained_variance_ratio_):
		ax.text(i-0.40, ax.get_ylim()[1] + 0.05, "Explained Variance\n          %.4f"%(ev))

	# Return a concatenated DataFrame
	return pd.concat([variance_ratios, components], axis = 1)

## New Plot function that splits into 5 at a time

def pca_results2(good_data, pca):
	'''
	Create a DataFrame of the PCA results
	Includes dimension feature weights and explained variance
	Visualizes the PCA results
	'''



    # Dimension indexing
	dimensions = dimensions = ['Dimension {}'.format(i) for i in range(1,len(pca.components_)+1)]

	# PCA components
	components = pd.DataFrame(np.round(pca.components_, 4), columns = good_data.keys())
	components.index = dimensions

	# PCA explained variance
	ratios = pca.explained_variance_ratio_.reshape(len(pca.components_), 1)
	variance_ratios = pd.DataFrame(np.round(ratios, 4), columns = ['Explained Variance'])
	variance_ratios.index = dimensions

	# Configure the number of dims to show per subplot
	dims_per_plot = dpp = 5

	# Prepare plot with appropriate number of subplots
	# Note: see [1]
	plot_rows = -(-len(dimensions) // dims_per_plot)
	fig, axes = plt.subplots(plot_rows, 1, figsize = (14,8*plot_rows))

	# For each subplot...
	for c, ax in enumerate(axes):

	    # Plot the appropriate components
	    components.iloc[c*dpp:c*dpp+dpp].plot(ax=ax, kind='bar');
	    ax.set_ylabel("Feature Weights")

	    # Configure the xticks
	    # Note: set_xticks is necessary for correct display of partially filled plots
	    ax.set_xticks(range(dpp+1))
	    ax.set_xticklabels(dimensions[c*dpp:c*dpp+dpp], rotation=0)

	    # Display the explained variance ratios
	    # Note: the ha and multialignment kwargs allow centering of (multiline) text
	    for i, ev in enumerate(pca.explained_variance_ratio_[c*dpp:c*dpp+dpp]):
	        ax.text(i, ax.get_ylim()[1] + 0.02,
	                "Explained Variance\n%.4f" % (ev),
	                ha='center', multialignment='center')

	# Done
	plt.show()


	# Return a concatenated DataFrame
	return pd.concat([variance_ratios, components], axis = 1)



def cluster_results(reduced_data, preds, centers, pca_samples):
	'''
	Visualizes the PCA-reduced cluster data in two dimensions
	Adds cues for cluster centers and student-selected sample data
	'''

	predictions = pd.DataFrame(preds, columns = ['Cluster'])
	plot_data = pd.concat([predictions, reduced_data], axis = 1)

	# Generate the cluster plot
	fig, ax = plt.subplots(figsize = (14,8))

	# Color map
	cmap = cm.get_cmap('gist_rainbow')

	# Color the points based on assigned cluster
	for i, cluster in plot_data.groupby('Cluster'):
	    cluster.plot(ax = ax, kind = 'scatter', x = 'Dimension 1', y = 'Dimension 2', \
	                 color = cmap((i)*1.0/(len(centers)-1)), label = 'Cluster %i'%(i), s=30);

	# Plot centers with indicators
	for i, c in enumerate(centers):
	    ax.scatter(x = c[0], y = c[1], color = 'white', edgecolors = 'black', \
	               alpha = 1, linewidth = 2, marker = 'o', s=200);
	    ax.scatter(x = c[0], y = c[1], marker='$%d$'%(i), alpha = 1, s=100);

	# Plot transformed sample points
	ax.scatter(x = pca_samples[:,0], y = pca_samples[:,1], \
	           s = 150, linewidth = 4, color = 'black', marker = 'x');

	# Set plot title
	ax.set_title("Cluster Learning on PCA-Reduced Data - Centroids Marked by Number\nTransformed Sample Data Marked by Black Cross");


def biplot(good_data, reduced_data, pca):
    '''
    Produce a biplot that shows a scatterplot of the reduced
    data and the projections of the original features.

    good_data: original data, before transformation.
               Needs to be a pandas dataframe with valid column names
    reduced_data: the reduced data (the first two dimensions are plotted)
    pca: pca object that contains the components_ attribute

    return: a matplotlib AxesSubplot object (for any additional customization)

    This procedure is inspired by the script:
    https://github.com/teddyroland/python-biplot
    '''

    fig, ax = plt.subplots(figsize = (14,8))
    # scatterplot of the reduced data
    ax.scatter(x=reduced_data.loc[:, 'Dimension 1'], y=reduced_data.loc[:, 'Dimension 2'],
        facecolors='b', edgecolors='b', s=70, alpha=0.5)

    feature_vectors = pca.components_.T

    # we use scaling factors to make the arrows easier to see
    arrow_size, text_pos = 7.0, 8.0,

    # projections of the original features
    for i, v in enumerate(feature_vectors):
        ax.arrow(0, 0, arrow_size*v[0], arrow_size*v[1],
                  head_width=0.2, head_length=0.2, linewidth=2, color='red')
        ax.text(v[0]*text_pos, v[1]*text_pos, good_data.columns[i], color='black',
                 ha='center', va='center', fontsize=18)

    ax.set_xlabel("Dimension 1", fontsize=14)
    ax.set_ylabel("Dimension 2", fontsize=14)
    ax.set_title("PC plane with original feature projections.", fontsize=16);
    return ax


# supervised learning helper functions


# Note: may need to edit labels

###########################################
# Suppress matplotlib user warnings
# Necessary for newer version of matplotlib
import warnings
warnings.filterwarnings("ignore", category = UserWarning, module = "matplotlib")
#
# Display inline matplotlib plots with IPython
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
###########################################

import matplotlib.pyplot as pl
import matplotlib.patches as mpatches
from sklearn.metrics import f1_score, accuracy_score


def distribution(data, transformed = False, dist_list=[]):
    """
    Visualization code for displaying skewed distributions of features
    """

    # Create figure
    fig = pl.figure(figsize = (11,5));

    # Skewed feature plotting

    # Need to generalize
    for i, feature in enumerate(dist_list):
        ax = fig.add_subplot(1, 2, i+1)
        ax.hist(data[feature], bins = 25, color = '#00A0A0')
        ax.set_title("'%s' Feature Distribution"%(feature), fontsize = 14)
        ax.set_xlabel("Value")
        ax.set_ylabel("Number of Records")
        ax.set_ylim((0, 2000))
        ax.set_yticks([0, 500, 1000, 1500, 2000])
        ax.set_yticklabels([0, 500, 1000, 1500, ">2000"])

    # Plot aesthetics

    # Need to generalize
    if transformed:
        fig.suptitle("Log-transformed Distributions of Continuous Data", \
            fontsize = 16, y = 1.03)
    else:
        fig.suptitle("Skewed Distributions of Continuous Data", \
            fontsize = 16, y = 1.03)

    fig.tight_layout()
    fig.show()


def evaluate(results, accuracy, f1):
    """
    Visualization code to display results of various learners.

    inputs:
      - learners: a list of supervised learners
      - stats: a list of dictionaries of the statistic results from 'train_predict()'
      - accuracy: The score for the naive predictor
      - f1: The score for the naive predictor
    """

    # Create figure
    fig, ax = pl.subplots(2, 3, figsize = (11,7))

    # Constants
    bar_width = 0.3
    colors = ['#A00000','#00A0A0','#00A000']

    # Super loop to plot four panels of data
    for k, learner in enumerate(results.keys()):
        for j, metric in enumerate(['train_time', 'acc_train', 'f_train', 'pred_time', 'acc_test', 'f_test']):
            for i in np.arange(3):

                # Creative plot code
#                 ax[j/3, j%3].bar(i+k*bar_width, results[learner][i][metric], width = bar_width, color = colors[k])
#                 ax[j/3, j%3].set_xticks([0.45, 1.45, 2.45])
#                 ax[j/3, j%3].set_xticklabels(["1%", "10%", "100%"])
#                 ax[j/3, j%3].set_xlabel("Training Set Size")
#                 ax[j/3, j%3].set_xlim((-0.1, 3.0))


                ax[int(j/3), j%3].bar(i+k*bar_width, results[learner][i][metric], width = bar_width, color = colors[k])
                ax[int(j/3), j%3].set_xticks([0.45, 1.45, 2.45])
                ax[int(j/3), j%3].set_xticklabels(["1%", "10%", "100%"])
                ax[int(j/3), j%3].set_xlabel("Training Set Size")
                ax[int(j/3), j%3].set_xlim((-0.1, 3.0))

    # Add unique y-labels
    ax[0, 0].set_ylabel("Time (in seconds)")
    ax[0, 1].set_ylabel("Accuracy Score")
    ax[0, 2].set_ylabel("F-score")
    ax[1, 0].set_ylabel("Time (in seconds)")
    ax[1, 1].set_ylabel("Accuracy Score")
    ax[1, 2].set_ylabel("F-score")

    # Add titles
    ax[0, 0].set_title("Model Training")
    ax[0, 1].set_title("Accuracy Score on Training Subset")
    ax[0, 2].set_title("F-score on Training Subset")
    ax[1, 0].set_title("Model Predicting")
    ax[1, 1].set_title("Accuracy Score on Testing Set")
    ax[1, 2].set_title("F-score on Testing Set")

    # Add horizontal lines for naive predictors
    ax[0, 1].axhline(y = accuracy, xmin = -0.1, xmax = 3.0, linewidth = 1, color = 'k', linestyle = 'dashed')
    ax[1, 1].axhline(y = accuracy, xmin = -0.1, xmax = 3.0, linewidth = 1, color = 'k', linestyle = 'dashed')
    ax[0, 2].axhline(y = f1, xmin = -0.1, xmax = 3.0, linewidth = 1, color = 'k', linestyle = 'dashed')
    ax[1, 2].axhline(y = f1, xmin = -0.1, xmax = 3.0, linewidth = 1, color = 'k', linestyle = 'dashed')

    # Set y-limits for score panels
    ax[0, 1].set_ylim((0, 1))
    ax[0, 2].set_ylim((0, 1))
    ax[1, 1].set_ylim((0, 1))
    ax[1, 2].set_ylim((0, 1))

    # Create patches for the legend
    patches = []
    for i, learner in enumerate(results.keys()):
        patches.append(mpatches.Patch(color = colors[i], label = learner))
    pl.legend(handles = patches, bbox_to_anchor = (-.80, 2.53), \
               loc = 'upper center', borderaxespad = 0., ncol = 3, fontsize = 'x-large')

    # Aesthetics
    pl.suptitle("Performance Metrics for Three Supervised Learning Models", fontsize = 16, y = 1.10)
    pl.tight_layout()
    pl.show()


def feature_plot(importances, X_train, y_train):

    # Display the five most important features
    indices = np.argsort(importances)[::-1]
    columns = X_train.columns.values[indices[:5]]
    values = importances[indices][:5]

    # Creat the plot
    fig = pl.figure(figsize = (9,5))
    pl.title("Normalized Weights for First Five Most Predictive Features", fontsize = 16)
    pl.bar(np.arange(5), values, width = 0.6, align="center", color = '#00A000', \
          label = "Feature Weight")
    pl.bar(np.arange(5) - 0.3, np.cumsum(values), width = 0.2, align = "center", color = '#00A0A0', \
          label = "Cumulative Feature Weight")
    pl.xticks(np.arange(5), columns)
    pl.xlim((-0.5, 4.5))
    pl.ylabel("Weight", fontsize = 12)
    pl.xlabel("Feature", fontsize = 12)

    pl.legend(loc = 'upper center')
    pl.tight_layout()
    pl.show()


#### New helper functions

# finds continuous fields that are correlated based on pearson corelation
# returns dict with field and list of correlated fields

# Note: maybe add code that removes key from list in dicts
# ex. so field1 isn't shown to be correlated with field1

def contCorDct(dat_df,cntLst,thrsh):


    ScaledDeptDf=dat_df.copy()

    ScaledDeptDf=ScaledDeptDf[cntLst]
    ScaledDeptDf=scaleData(ScaledDeptDf,ScaledDeptDf.columns.tolist())
    corrDf=(ScaledDeptDf.corr()>thrsh).mul(ScaledDeptDf.corr().index.values,0)

    corrLst=[corrDf[corrDf[x]!=''][x].tolist() for x in corrDf.columns.tolist()]
    corrdict=dict(zip(corrDf.columns.tolist(),corrLst))

    return corrdict


# finds correlation between categorical and continuous variables
# returns dict with categorical field and all correlated continuous fields

def catConCorDct(datDf,CtLst,CntLst):

    # tstLst=['Super_Region','Region','District']


    tstLst=CtLst


    import statsmodels.api as sm
    from statsmodels.formula.api import ols

    emptDct=dict()#{}

    for j in tstLst: #catLst:

        try:

    # test for one catvar
            #catvar2=j #'MACYS_DIVISION'

            emptCorLst=[]

            for i in CntLst:


                # subsetting data for one categorical column and one continuous column
                data2=datDf.copy()[[j,i]]#catCorDf.copy()[[catVar2,i]]
                data2[j]=data2[j].astype('category')

                argStr="Q('"+i+"') ~ Q('"+j+"')"

                mod = ols(argStr,data=data2).fit()

                aov_table = sm.stats.anova_lm(mod, typ=2)

                if aov_table['PR(>F)'][0] < 0.05:
                    #print(i)
                    emptCorLst.append(i)
                    #print(emptCorLst)
            #emptDct=emptDct.update({j:emptCorLst})
            emptDct.update({j:emptCorLst})
        except Exception as e:
            print(argStr)
            print('')
            print(e)

    return emptDct

# finds indices which are outliers for continuous field based on tukeys method
# returns dict with continuous field and indices that are outliers

def OtlrFn(df,cntLst):

    tstLst=cntLst

    tstdf_o=df.copy()

    tstdf_o=tstdf_o[tstLst]

    OtlrDct={}


    # For each feature find the data points with extreme high or low values
    for feature in tstdf_o.keys():

        # TODO: Calculate Q1 (25th percentile of the data) for the given feature
        Q1 = np.percentile(tstdf_o[feature], 25)

        # TODO: Calculate Q3 (75th percentile of the data) for the given feature
        Q3 = np.percentile(tstdf_o[feature], 75)

        # TODO: Use the interquartile range to calculate an outlier step (1.5 times the interquartile range)
        step = 1.5*(Q3-Q1)

        OtlrDct[feature]=tstdf_o[~((tstdf_o[feature] >= Q1 - step) & (tstdf_o[feature] <= Q3 + step))].index.tolist()

    return OtlrDct


# function to remove outliers from dataframe

def rm_otlr(df,fld):

    df2=df.copy()

    # dict with key continuous field and value list of hostnameHash that are outliers for field
    Olr_dct=OtlrFn(df=df2,cntLst=[fld])

    # printing the field and len of list of outliers
    for i,v in Olr_dct.items():
        print(i)
        print(len(v))

    u=Olr_dct[fld]

    df2=df2[~df2.index.isin(u)]

    print(df2.shape[0])

    return df2




# function to help classify fields

def LstFnc(Ldf,tct):



    df=Ldf.copy()

    LstCol=df.columns.tolist()



    # LstCat = categorical fields-fields that have fewer unique values than 10% records
    LstCat=df.nunique()[df.nunique()<round(tct*df.shape[0])].index.tolist()

    # # lstCont = continuous fields-fields that are int or float
    LstCont=df._get_numeric_data().columns.tolist()

    # lstId = id fields-fields that have more unique values than 10% of records
    LstId = df.nunique()[df.nunique()>round(tct*df.shape[0])].index.tolist()


    # lstMssng = fields that are missing more than 50%-make threshold adjustable
    LstMssng = df.apply(lambda x: float(sum(x.isnull()))/len(x))[df.apply(lambda x: float(sum(x.isnull()))/len(x))>0.5]\
    .index.tolist()

    # SigMssng = fields that are missing more than 5%-make threshold adjustable
    SigMssng = df.apply(lambda x: float(sum(x.isnull()))/len(x))[df.apply(lambda x: float(sum(x.isnull()))/len(x))>0.05]\
    .index.tolist()

    fcat=set(LstCat)-set(LstMssng)

    fcont=set(LstCont)-set(LstMssng)

    fid=set(LstId)-set(LstMssng)

    print('Possible Field classifications:')
    print('')
    print('categorical fields-fields that have fewer unique values than 10% records:')
    print(len(LstCat))
    print(LstCat)
    print('')
    print('continuous fields-fields that are int or float:')
    print(len(LstCont))
    print(LstCont)
    print('')
    print('id fields-fields that have more unique values than 10% of records:')
    print(len(LstId))
    print(LstId)
    print('')
    print('fields that are missing more than 50%:')
    print(len(LstMssng))
    print(LstMssng)
    print('')
    print('fields that are missing more than 5%:')
    print(len(SigMssng))
    print(SigMssng)
    print('')
    print('filled categorical:')
    print(len(fcat))
    print(fcat)
    print('')
    print('filled continuous:')
    print(len(fcont))
    print(fcont)
    print('')
    print('filled id:')
    print(len(fid))
    print(fid)
    print('')


# kmeans cluster pipeline
def KmnsClstr(kdf,cLst,clstN,pCmp=None):

    # create copy of original data
    df=kdf.copy()


    if pCmp==None:

        # Apply MinMax scaler to data
        scaled_data=scaleData(s_df=df[cLst],list_cont=cLst)

        # easy to adjust for pca
        reduced_data1=scaled_data

        # K-means with specific number of clusters
        clusterer = KMeans(n_clusters=clstN).fit(reduced_data1)
        preds = clusterer.predict(reduced_data1)
        centers = clusterer.cluster_centers_

        # checking number in each cluster
        clustered_data=reduced_data1.copy()
        clustered_data['Cluster']=preds

        # updated 10/8/19
        print('')
        score = silhouette_score(reduced_data1, preds, metric='euclidean')
        print("For n_clusters = {}. The average silhouette_score is : {}".format(clstN, score))
        print('')

        print('Number in cluster:')

        cntrN=clustered_data.groupby('Cluster').count().copy()
        cntrN1=pd.DataFrame(cntrN[cntrN.columns[0]])
        cntrN1.columns=['Number']

        display(cntrN1.sort_values(by=['Number'],ascending=False))


        # compare centers to means from data



        # TODO: Inverse transform the centers

        # re-fitting MinMaxScaler() for inverse transform
        sclr = MinMaxScaler()
        sclr.fit_transform(df[cLst])

        centers2 = sclr.inverse_transform(centers)
        # centers2 = pca.inverse_transform(centers)



        # Display the true centers

        segments = ['Segment {}'.format(i) for i in range(0,len(centers2))]
        #true_centers = pd.DataFrame(np.round(centers2), columns = scaled_data.keys())
        true_centers = pd.DataFrame(centers2, columns = scaled_data.keys())
        true_centers.index = segments


        pd.set_option('display.max_columns', true_centers.shape[1])


        print('Ratio Centers/Mean:')

        display(pd.concat([pd.DataFrame({'std/mean':df[cLst].std()/df[cLst].mean()}).T,\
                           true_centers/df[cLst].mean()],\
                axis=0))

        print('Cluster Centers:')
        display(true_centers)

        # adding original data for easy comparison
        print('General population:')

        display(df[cLst].describe())

    elif pCmp!=None:

        # Apply MinMax scaler to data
        scaled_data=scaleData(s_df=df[cLst],list_cont=cLst)


        ####specify number of components for pca

        colList=['Dimensnion_'+str(i+1) for i in range(pCmp)]

        good_data=scaled_data

        # TODO: Apply PCA by fitting the good data with only two dimensions
        pca = PCA(n_components=pCmp).fit(good_data)

        # TODO: Transform the good data using the PCA fit above
        reduced_data1 = pca.transform(good_data)

        # Create a DataFrame for the reduced data
        reduced_data1 = pd.DataFrame(reduced_data1, columns = colList)



        # easy to adjust for pca
        #reduced_data1=scaled_data

        #####

        # K-means with specific number of clusters
        clusterer = KMeans(n_clusters=clstN).fit(reduced_data1)
        preds = clusterer.predict(reduced_data1)
        centers = clusterer.cluster_centers_

        # checking number in each cluster
        clustered_data=reduced_data1.copy()
        clustered_data['Cluster']=preds

        # updated 10/8/19
        print('')
        score = silhouette_score(reduced_data1, preds, metric='euclidean')
        print("For n_clusters = {}. The average silhouette_score is : {}".format(clstN, score))
        print('')

        print('Number in cluster:')

        cntrN=clustered_data.groupby('Cluster').count().copy()
        cntrN1=pd.DataFrame(cntrN[cntrN.columns[0]])
        cntrN1.columns=['Number']

        display(cntrN1.sort_values(by=['Number'],ascending=False))


        # compare centers to means from data



        # TODO: Inverse transform the centers

        # re-fitting MinMaxScaler() for inverse transform
        sclr = MinMaxScaler()
        sclr.fit_transform(df[cLst])


        #### PCA inverse transform
        centers1 = pca.inverse_transform(centers)

        centers2 = sclr.inverse_transform(centers1)
        # centers2 = pca.inverse_transform(centers)
        ####



        # Display the true centers

        segments = ['Segment {}'.format(i) for i in range(0,len(centers2))]
        #true_centers = pd.DataFrame(np.round(centers2), columns = scaled_data.keys())
        true_centers = pd.DataFrame(centers2, columns = scaled_data.keys())
        true_centers.index = segments


        pd.set_option('display.max_columns', true_centers.shape[1])


        print('Ratio Centers/Mean:')

        display(pd.concat([pd.DataFrame({'std/mean':df[cLst].std()/df[cLst].mean()}).T,\
                           true_centers/df[cLst].mean()],\
                axis=0))

        print('Cluster Centers:')
        display(true_centers)

        # adding original data for easy comparison
        print('General population:')

        display(df[cLst].describe())
