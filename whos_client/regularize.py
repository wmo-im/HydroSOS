import pandas
import argparse
import os

def regularizeDir(input_dir : str, output_dir : str):
    if input_dir == output_dir:
        raise ValueError("input_dir and output_dir must be different")
    for f in os.listdir(input_dir):
        if f.endswith('.csv'):
            regularize(os.path.join(input_dir, f), os.path.join(output_dir,f))

def regularize(input : str, output : str):
    # read om-api-client data .csv (cols: date (iso format),value (float))
    try:
        flowdata = pandas.read_csv(input)
    except pandas.errors.EmptyDataError as e:
        print("No data found in file: %s. Skippping" % input)
        return
    # set column names: date,flow
    flowdata.columns = ['date','flow']
    flowdata['date'] = pandas.to_datetime(flowdata['date'], format="ISO8601")
    flowdata.set_index("date", inplace=True)
    # regularize to daily step, average rows of same date, remove nulls
    flowdata = flowdata.resample('D').mean().dropna()
    flowdata.reset_index(inplace=True)
    # output date format "%d/%m/%Y"
    flowdata['date'] = flowdata['date'].dt.strftime('%d/%m/%Y')
    flowdata.to_csv(open(output, "w"), index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        prog='regularize.py',
                        description='regularize csv timeseries to daily step and save with HydroSOS format',
                        epilog='Bianchi, J, 20250717')

    parser.add_argument('input', help='input csv file with dates in ISO format. If a directory is passed, reads all .csv files in that directory.')
    parser.add_argument('output', help='output file or directory')

    args = parser.parse_args()

    if os.path.isdir(args.input):
        if not os.path.isdir(args.output):
            raise ValueError("If input is a directory, output must also be a directory")
        regularizeDir(args.input, args.output)
    else:
        regularize(args.input, args.output)