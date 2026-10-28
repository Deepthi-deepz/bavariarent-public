"""Create explicitly fictional BavariaRent demo records (no Kaggle data used)."""
from pathlib import Path
import csv
import random

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data' / 'sample' / 'synthetic_bavaria_demo.csv'


def make_demo_data(path=OUTPUT, n=240):
    rng = random.Random(20261028)
    groups = ('Demo Area A', 'Demo Area B', 'Demo Area C', 'Demo Area D')
    dates = ('2018-09-01', '2019-05-01', '2019-10-01', '2020-02-01')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as fp:
        writer = csv.DictWriter(fp, fieldnames=('regio1','regio2','baseRent','livingSpace','base_rent_per_sqm','date'))
        writer.writeheader()
        for i in range(n):
            area = float(rng.randint(25, 135))
            euro_per_m2 = round(rng.uniform(8.0, 19.0) + (i % 4) * 1.2, 2)
            rent = round(area * euro_per_m2, 2)
            writer.writerow({'regio1': 'Bayern', 'regio2': groups[i % 4],
                             'baseRent': f'{rent:.2f}', 'livingSpace': f'{area:.2f}',
                             'base_rent_per_sqm': f'{rent/area:.8f}',
                             'date': dates[i % 4]})
    return path


if __name__ == '__main__':
    print('Created SYNTHETIC demo data:', make_demo_data())
