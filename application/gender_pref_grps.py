import pandas as pd

in_path = "C:/Users/Alisa/Downloads/Matches 9_23 - Sheet1.csv"

# split csv into three groups
male_male_str = '(Gender == "Male" & GenderPref == "Male")'
female_female_str = '(Gender == "Female" & GenderPref == "Female")'
male_female_str = '(Gender == "Male" & GenderPref == "Female")'
female_male_str = '(Gender == "Female" & GenderPref == "Male")'

def split_into_groups(df):
    male_male_df = df.query(male_male_str)
    #print(male_male_df)
    female_female_df = df.query(female_female_str)
    #print(female_female_df)

    male_female_df = df.query(male_female_str)

    female_male_df = df.query(female_male_str)

    male_female_female_male_df = df.query(male_female_str+'|'+female_male_str)
    #print(male_female_female_male_df)

    other_pref_df = df.query('(Gender != "Male" | GenderPref != "Male") & (Gender != "Female" | GenderPref != "Female") & (Gender != "Male" | GenderPref != "Female") & (Gender != "Female" | GenderPref != "Male")')
    #print(other_pref_df)
    other_male_df = other_pref_df.query('Gender == "Male"')
    other_female_df = other_pref_df.query('Gender == "Female"')

    
    age_groups = male_female_female_male_df["Age"].unique() # list of all unique age groups
        
    for age in age_groups:
        male_group = male_female_df.query('Age == "' + age + '"')
        female_group = female_male_df.query('Age == "' + age + '"')
        male_num = len(male_group)
        female_num = len(female_group)
        extra = abs(male_num - female_num)

        part_df = None
        if male_num > female_num:
            part_df = (other_female_df.query('Age == "' + age + '"')).head(extra)
        elif female_num > male_num:
            part_df = (other_male_df.query('Age == "' + age + '"')).head(extra)
        if extra != 0:
            male_female_female_male_df = pd.concat([male_female_female_male_df, part_df])
            other_pref_df = pd.concat([other_pref_df, part_df]).drop_duplicates(keep=False)
    
    return [male_male_df, male_female_female_male_df, female_female_df, other_pref_df]

#df = pd.read_csv(in_path)
#new_groups = split_into_groups(df)
#total_df = pd.concat(new_groups)
#new_groups[0].to_csv('mm_output_grps.csv', index=False)
#new_groups[1].to_csv('mf_output_grps.csv', index=False)
#new_groups[2].to_csv('ff_output_grps.csv', index=False)
#new_groups[3].to_csv('other_output_grps.csv', index=False)

#df = df.assign(score = [''] * len(df))
#to_add = df[['Gender']*3].apply(lambda x: ' '.join(x), axis=1)
#df['score'] = df['score'].str.cat(to_add, sep=" ", na_rep = "")
#print(df['score'])