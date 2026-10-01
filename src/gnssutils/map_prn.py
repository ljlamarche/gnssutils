# map_prn.py
# functions for converting GPS PRN numbers to NORAD satellite ID

# IMPORTANT: PRNs are reassigned as GPS satellites are comissioned/decomissioned
# This means a particular PRN may refer to different physical satellites
#   at different points in time.  NORAD IDs are associated with physical
#   satellites and do NOT change.  Time is required to properly map PRNs
#   to NORAD IDs.

from ftplib import FTP
import datetime as dt
import numpy as np
import pandas as pd
import io
import warnings
import requests


def time_convert(time_string):
    # Convert YYYY:DDD:SSSSS to datetime format
    # YYYY: year
    # DDD: day of year
    # SSSSS: second of day

    if time_string == '0000:000:00000':
        date = dt.datetime.now(tz=dt.timezone.utc)
    else:
        date = dt.datetime.strptime(time_string[:8], '%Y:%j')
        date = date.replace(tzinfo=dt.timezone.utc)
        seconds = int(time_string[-5:])
        date += dt.timedelta(seconds=seconds)

    return date

def retrieve_prn_mapping_info(metadata_file=None):

    if metadata_file:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            filetext = f.read()
    else:
        r = requests.get('https://files.igs.org/pub/station/general/igs_satellite_metadata.snx')
        r.encoding = 'utf-8'
        filetext = r.text

    # Extract SATELLITE/IDENTIFIER table
    sidx = filetext.find('+SATELLITE/IDENTIFIER')
    eidx = filetext.find('-SATELLITE/IDENTIFIER')
    # messy one-line to remove comment section at end of each line - doesn't parse correctly
    block = '\n'.join([l[:39] for l in filetext[sidx:eidx].splitlines()[1:]])
    # Convert to pandas dataframe
    identifier_table = pd.read_table(io.StringIO(block), 
                                     sep=r'\s+', comment='*',
                                     names=['SVN','COSPAR','NORAD','Block'])

    # Extract SATELLITE/PRN table
    sidx = filetext.find('+SATELLITE/PRN')
    eidx = filetext.find('-SATELLITE/PRN')
    # messy one-line to remove comment section at end of each line - doesn't parse correctly
    block = '\n'.join([l[:40] for l in filetext[sidx:eidx].splitlines()[1:]])
    # Convert to pandas dataframe
    prn_table = pd.read_table(io.StringIO(block), 
                              sep=r'\s+', comment='*',
                              names=['SVN','Start','End','PRN'],
                              converters={'Start':time_convert, 'End':time_convert})

    return identifier_table, prn_table


def find_date_index(startdates, enddates, targdate):
    # find the index where the target date is between the start and end dates
    # raises an error if the date does not correspond to a range in the PRN table

    try:
        tidx = np.argwhere((targdate>=startdates) & (targdate<enddates)).flatten()[0]
    except IndexError:
        raise ValueError('The specified PRN was not used on {}!'.format(targdate.isoformat()))

    return tidx


def prn2norad(prn, date, metadata_file=None):
    # map PRN to NORAD SAT ID

    date = date.replace(tzinfo=dt.timezone.utc)
    
    identifier_table, prn_table = retrieve_prn_mapping_info(metadata_file=metadata_file)

    #pd.set_option('display.max_columns', None)

    subtable = prn_table.loc[prn_table['PRN']==prn]
    #print(subtable)
    #svn = subtable.loc[(subtable['Start']<=date) & (subtable['End']>date), 'SVN']
    #print(svn)
    try:
        svn = subtable.loc[(subtable['Start']<=date) & (subtable['End']>date), 'SVN'].iat[0]

        norad = identifier_table.loc[identifier_table['SVN']==svn, 'NORAD'].iat[0]
    
        return norad

    except IndexError as e:
        print(e)
        warnings.warn(f'No PRN {prn} available for {date}!')
        return None


#    idx = find_date_index(mapping_dict[prn]['STARTTIME'], mapping_dict[prn]['ENDTIME'], date)
#    return mapping_dict[prn]['NORADID'][idx]


def prn2svn(prn, date):
    # map PRN to SVN

    mapping_dict = retrieve_prn_mapping_info()
    idx = find_date_index(mapping_dict[prn]['STARTTIME'], mapping_dict[prn]['ENDTIME'], date)

    return mapping_dict[prn]['SVN'][idx]





if __name__=='__main__':

    print(prn2norad('G18', dt.datetime(2019,2,1), metadata_file='igs_satellite_metadata.snx'))
    #print(prn2svn(18, dt.datetime(2016,2,1)))
