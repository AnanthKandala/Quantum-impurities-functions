import os


# Important functions:
    # - write_in
    # - write_SLURM
    # - write_launch
    # - write_g_spec
    # - write_extract 




#prints ander.in:
def write_in(infile,e_d,U,Gamma, Delta,g, K, threshold_min, threshold_max, var_min, var_max):
    with open(infile, 'w') as file1:
         file1.write('{0} {1} 1d-13    100'.format(var_min, var_max)+'\n')
         file1.write(f' 0      0  {threshold_min} {threshold_max}     -3'+'\n')
         file1.write(f'{e_d} {U} {Gamma}  0.0    0.0    0.0'+'\n')
         file1.write(f'0.0    0.0    {g}    0.0    0.0    1.0      0'+'\n')
         file1.write('0.0    0.0    0.0    0.0    0.0    0.0    0.0'+'\n')
         file1.write(f'{Delta}    0.0    0.0    0.0                          1'+'\n')
         file1.write('9.0    0.0    0.0          1d-6         1d-20'+'\n')
         file1.write(f'0     50      0   {K}      0      1      0     0'+'\n')
         file1.write('5    0.6'+'\n')
    return


#prints SLURM script:
def write_SLURM(fl,title,direc):
    y=str(os.getcwd())
    with open(fl,'w') as file2:
         file2.write('#!/bin/bash'+'\n')
         file2.write('#SBATCH --job-name={}   # Job name'.format(title)+'\n')
         file2.write('#SBATCH --mail-type=FAIL,END          # Mail events (NONE, BEGIN, END, FAIL, ALL) '+'\n')
         file2.write('#SBATCH --account=physics-dept'+'\n')
         file2.write('#SBATCH --qos=physics-dept'+'\n')
         file2.write('#SBATCH --mail-user=swimzebra@protonmail.com     # Where to send mail'+'\n')
         file2.write('#SBATCH --ntasks=1                    # Run on a single CPU'+'\n')
         file2.write('#SBATCH --mem=1Gb                     # Job memory request'+'\n')
         file2.write('#SBATCH --time=4:00:00               # Time limit hrs:min:sec'+'\n')
         file2.write('#SBATCH --output=script_output   # Standard output and error log'+'\n')
         file2.write('pwd; hostname; date'+'\n')
         file2.write('module load gcc/8.2.0'+'\n')
         file2.write('module load lapack/3.8.0'+'\n')
         string=y+f'/{direc}/ander'
         file2.write(string+'\n')
         file2.write('date')


#prints launch script:
def write_launch_tcsh(infile, var):
    direct = f'{var}=$var/'
    y = str(os.getcwd())
    with open(infile, 'w') as file3:
        file3.write(f"""#!/bin/tcsh
set var = `cat running_var.txt`
foreach var ($var)
    cd "{y}/{direct}"
    sbatch SLURM
end
        """)


#Function that writes the gspec file which runs the python file g_spectrum.py
#g_spectrum.py:
    # -renames the last ander.out files
    # copies the last files to last_runs directory
#variable is the name of the fixed_variable.
def write_gspec(infile, variable):
    pwd = str(os.getcwd())
    with open(infile, 'w') as f:
        f.write(f"""#!/bin/tcsh
set arr = `cat var_completed.txt`
foreach var ($arr)
    cd {pwd}/{variable}=$var
    python g_spectrum.py
end
cd {pwd}/combine
source extract.sh
""")


#Function that writes extract.sh script which locates the runs closest to the critical point and extracts the levels using aextr.
def write_extract(outfile, fixed_variable):
    script = f'''#!/bin/tcsh

set dir0=`echo $cwd | awk -F'/' '{{print $(NF-1)}}'`"_levels"
mkdir -p $dir0

# Copy var_completed.txt to the $dir0 directory
cp ../var_completed.txt $dir0/.

# Read the values from var_completed.txt into the arr list
set arr = (`cat $dir0/var_completed.txt | awk '{{print $1}}'`)

# Iterate over the values in arr
foreach i ($arr)
    # Copy the directory structure and files from ../{fixed_variable}=$i/last_runs/ to $dir0/{fixed_variable}=$i/
    cp -r ../{fixed_variable}=$i/last_runs/ $dir0/{fixed_variable}=$i/

    # Iterate over the 'min' and 'max' keywords
    foreach k ('min' 'max')
        # Execute the aextr command
        aextr -1 3.0 < $dir0/{fixed_variable}=$i/$k.out > $dir0/{fixed_variable}=$i/$k.levels

        # Remove the original output file
        rm -rf $dir0/{fixed_variable}=$i/$k.out
    end

    echo $i
end
cp -r $dir0 
'''
    
    with open(outfile, 'w') as file:
        file.write(script)
    return

