import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from bavariarent.analytics import load_bavaria, regional_summary, size_summary, observation_summary

@pytest.fixture
def sample(tmp_path):
    df = pd.DataFrame({'regio1':['Bayern']*3, 'regio2':['A','A','B'],
                       'baseRent':[500,1000,800], 'livingSpace':[50,100,40],
                       'base_rent_per_sqm':[10.,10.,20.],
                       'date':['2019-05','2019-05','2020-02']})
    p=tmp_path/'data.csv';df.to_csv(p,index=False);return p

def test_valid_input(sample):
    df=load_bavaria(sample)
    assert len(df)==3
    assert regional_summary(df).set_index('regio2').loc['A','listings']==2
    assert size_summary(df)['listings'].sum()==3
    assert observation_summary(df)['listings'].sum()==3

def test_inconsistent_price(sample):
    df=pd.read_csv(sample);df.loc[0,'base_rent_per_sqm']=100;df.to_csv(sample,index=False)
    with pytest.raises(ValueError, match='differs'):
        load_bavaria(sample)

def test_wrong_region(sample):
    df=pd.read_csv(sample);df.loc[0,'regio1']='Berlin';df.to_csv(sample,index=False)
    with pytest.raises(ValueError, match='Bayern'):
        load_bavaria(sample)
