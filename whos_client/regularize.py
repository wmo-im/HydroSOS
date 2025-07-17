import pandas
import argparse

def regularize(input : str, output : str):
    # read om-api-client data .csv (cols: date (iso format),value (float))
    flowdata = pandas.read_csv(input)
    # set column names: date,flow
    flowdata.columns = ['date','flow']
    flowdata['date'] = pandas.to_datetime(flowdata['date'], format="ISO8601")
    flowdata.set_index("date", inplace=True)
    # regularize to daily step, average rows of same date
    flowdata = flowdata.resample('D').mean()
    flowdata.reset_index(inplace=True)
    # output date format "%d/%m/%Y"
    flowdata['date'] = flowdata['date'].dt.strftime('%d/%m/%Y')
    flowdata.to_csv(open(output, "w"), index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                        prog='regularize.py',
                        description='regularize csv timeseries to daily step and save with HydroSOS format',
                        epilog='Bianchi, J, 20250717')


    parser.add_argument('input', help='input csv file with dates in ISO format')        
    parser.add_argument('output', help='output file')  

    args = parser.parse_args()

    regularize(args.input, args.output)