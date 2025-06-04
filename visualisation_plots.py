import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

# Set a universal style
sns.set(style="whitegrid", palette="muted", color_codes=True)

def filter_warsaw(df):
    """Filter only rows from Warsaw (non-null district)."""
    return df[df['district'].notnull()]

def plot_vehicle_class_distribution(df):
    """Barplot of vehicle class counts by district."""
    df_warsaw = filter_warsaw(df)
    df_grouped = df_warsaw.groupby('district')[[
        'class_distribution_0_count', 'class_distribution_1_count'
    ]].sum().reset_index().melt(id_vars='district', var_name='class', value_name='count')

    class_map = {
        'class_distribution_0_count': 'Large Vehicle',
        'class_distribution_1_count': 'Small Vehicle'
    }
    df_grouped['class'] = df_grouped['class'].map(class_map)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_grouped, x='district', y='count', hue='class')
    plt.xticks(rotation=45)
    plt.title('Vehicle Class Distribution by District')
    plt.tight_layout()
    plt.show()

def plot_confidence_distributions(df):
    """Boxplots of confidence statistics by district."""
    df_warsaw = filter_warsaw(df)

    plt.figure(figsize=(14, 6))
    sns.boxplot(data=df_warsaw, x='district', y='avg_confidence')
    plt.xticks(rotation=45)
    plt.title('Average Confidence Score by District')
    plt.tight_layout()
    plt.show()

def plot_avg_mask_ratio(df):
    """Boxplot of mask coverage by district."""
    df_warsaw = filter_warsaw(df)

    plt.figure(figsize=(14, 6))
    sns.boxplot(data=df_warsaw, x='district', y='avg_mask_ratio')
    plt.xticks(rotation=45)
    plt.title('Average Mask Ratio by District')
    plt.tight_layout()
    plt.show()

def plot_mask_coverage_distributions(df):
    """Boxplot of mask coverage by district."""
    df_warsaw = filter_warsaw(df)

    plt.figure(figsize=(14, 6))
    sns.boxplot(data=df_warsaw, x='district', y='mask_coverage_pct')
    plt.xticks(rotation=45)
    plt.title('Mask Coverage Percentage by District')
    plt.tight_layout()
    plt.show()

def plot_conf_vs_mask_ratio(df):
    """Scatterplot of confidence vs mask ratio colored by district."""
    df_warsaw = filter_warsaw(df)

    fig = px.scatter(
        df_warsaw, x='avg_confidence', y='avg_mask_ratio', color='district',
        title='Confidence vs. Mask Ratio by District',
        labels={'avg_confidence': 'Average Confidence', 'avg_mask_ratio': 'Average Mask Ratio'},
        opacity=0.6
    )
    fig.show()

def plot_high_vs_low_conf_counts(df):
    """Stacked bar chart of high/low confidence detections by district."""
    df_warsaw = filter_warsaw(df)

    grouped = df_warsaw.groupby('district')[['high_conf_boxes_count', 'low_conf_boxes_count']].sum().reset_index()
    grouped.set_index('district').plot(kind='bar', stacked=True, figsize=(12, 6), colormap='Set2')
    plt.title('High vs. Low Confidence Boxes Count by District')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_detection_stats_heatmap(df):
    """Heatmap of average detection stats across districts."""
    df_warsaw = filter_warsaw(df)
    stat_cols = [
        'avg_confidence', 'avg_mask_ratio', 'high_conf_avg_confidence',
        'low_conf_avg_confidence', 'high_conf_std_confidence', 'low_conf_std_confidence'
    ]
    grouped = df_warsaw.groupby('district')[stat_cols].mean()
    plt.figure(figsize=(12, 8))
    sns.heatmap(grouped, annot=True, cmap='viridis')
    plt.title('Heatmap of Detection Stats by District')
    plt.tight_layout()
    plt.show()

def plot_mask_ratio_distribution(df):
    """Plot mask ratio distribution bins by district."""
    df_warsaw = filter_warsaw(df)
    bins = [
        'mask_ratio_distribution_0-25%', 'mask_ratio_distribution_25-50%',
        'mask_ratio_distribution_50-75%', 'mask_ratio_distribution_75-100%'
    ]
    df_bins = df_warsaw.groupby('district')[bins].mean().reset_index().melt(id_vars='district', var_name='bin', value_name='ratio')

    plt.figure(figsize=(14, 6))
    sns.barplot(data=df_bins, x='district', y='ratio', hue='bin')
    plt.xticks(rotation=45)
    plt.title('Average Mask Ratio Distribution by District')
    plt.tight_layout()
    plt.show()

def plot_geospatial_mask_coverage(df):
    """Geospatial scatter plot of confidence scores in Warsaw."""
    df_warsaw = filter_warsaw(df)
    fig = px.scatter_mapbox(
        df_warsaw, lat='latitude', lon='longitude', color='mask_coverage_pct',
        color_continuous_scale='YlOrRd', size='avg_confidence',
        hover_name='district', mapbox_style='carto-positron',
        title='Geospatial Distribution of Mask Coverage in Warsaw',
        zoom=10, height=600
    )
    fig.show()

def plot_vehicles_ratio(df):
    """Barplot of large-to-small vehicle ratio per district."""
    df_warsaw = filter_warsaw(df)
    df_ratio = df_warsaw.groupby('district').apply(
        lambda x: x['class_distribution_0_count'].sum() / x['class_distribution_1_count'].sum()
        if x['class_distribution_1_count'].sum() != 0 else np.nan
    ).reset_index(name='large_to_small_ratio')

    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_ratio, x='district', y='large_to_small_ratio', palette='coolwarm')
    plt.title('Large to Small Vehicle Ratio by District')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
