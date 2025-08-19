#!/usr/bin/env python
# coding: utf-8

# In[1]:


def clean_dataframe(df):
    df = df.dropna()
    df.columns = [col.lower() for col in df.columns]
    return df

