import sqlite3
import os

# Function to create tables in the SQLite database
def create_tables():
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS AMINOACID_SUBSTITUTION_MODELS (
            name VARCHAR(30) PRIMARY KEY,
            author VARCHAR(50),
            publication_date DATE,
            article VARCHAR(255),
            taxonomic_group VARCHAR(50),
            comments VARCHAR(255)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SUBSTITUTION_MATRIX (
            binary_matrix BLOB PRIMARY KEY,
            model_id VARCHAR(30),
            FOREIGN KEY (model_id) REFERENCES AMINOACID_SUBSTITUTION_MODELS(name)
        )
    ''')
    
    conn.commit()
    conn.close()

# Function to insert model data into the database
def insert_models(models):
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()
    
    cursor.executemany('''
        INSERT INTO AMINOACID_SUBSTITUTION_MODELS (name, author, publication_date, article, taxonomic_group, comments)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', models)
    
    conn.commit()
    conn.close()

# Function to insert substitution matrices into the database
def insert_matrices(data_dir):
    conn = sqlite3.connect('models.db')
    cursor = conn.cursor()

    for file_name in os.listdir(data_dir):
        if file_name.endswith('.dat'):
            model_name = os.path.splitext(file_name)[0]
            file_path = os.path.join(data_dir, file_name)
            with open(file_path, 'rb') as binary_matrix:
                content_binary = binary_matrix.read()
                content = content_binary.decode('utf-8')
                cursor.execute('''
                    INSERT INTO SUBSTITUTION_MATRIX (binary_matrix, model_id)
                    VALUES (?, ?)
                ''', (content, model_name))

    conn.commit()
    conn.close()

# Model data
models = [
    ('cpREV', 'Adachi et al.', '2000', '10.1007/s002399910038', 'Chloroplast', 'Chloroplast matrix'),
    ('Dayhoff', 'Dayhoff et al.', '1978', 'http://compbio.berkeley.edu/class/c246/Reading/dayhoff-1978-apss.pdf', 'Nuclear', 'General matrix'),
    ('Dayhoff-DCMut', 'Kosiol and Goldman', '2005', 'https://academic.oup.com/mbe/article/22/2/193/963836?login=true', 'Nuclear', 'Revised Dayhoff matrix'),
    ('GMS', 'Grantham', '1974', 'https://www.science.org/doi/abs/10.1126/science.185.4154.862', 'General', 'General matrix'),
    ('JTT', 'Jones et al.', '1992', 'https://academic.oup.com/bioinformatics/article/8/3/275/193076?login=true', 'Nuclear', 'General Matrix'),
    ('JTTDCMut', 'Kosiol and Goldman', '2005', 'https://academic.oup.com/mbe/article/22/2/193/963836?login=true', 'Nuclear', 'Revised JTT matrix'),
    ('LG', 'Le and Gascuel', '2008', 'https://academic.oup.com/mbe/article/25/7/1307/1041491?login=true', 'Nuclear', 'General matrix'),
    ('Miyata', 'Nei and Li', '1979', 'https://www.pnas.org/doi/abs/10.1073/pnas.76.10.5269', 'Mitochondrial', 'Mitochondrial matrix'),
    ('mtART', 'Abascal et al.', '2007', 'https://academic.oup.com/mbe/article/15/12/1600/963095?login=true', 'Mitochondrial', 'Mitochondrial Arthropoda'),
    ('mtMAM', 'Yang et al.', '1998', 'https://academic.oup.com/mbe/article/15/12/1600/963095?login=true', 'Mitochondrial', 'Mitochondrial Mammalia'),
    ('mtREV24', 'Adachi and Hasegawa', '1996', 'https://link.springer.com/article/10.1007/BF02498640', 'Mitochondrial', 'Mitochondrial Vertebrate'),
    ('mtZOA', 'Rota-Stabelli et al.', '2009', 'https://www.sciencedirect.com/science/article/pii/S1055790309000165?via%3Dihub', 'Mitochondrial', 'Mitochondrial Metazoa (Animals)'),
    ('WAG', 'Whelan and Goldman', '2001', 'https://academic.oup.com/mbe/article/18/5/691/1018653', 'Nuclear', 'General matrix'),
    ('cpREV64', 'Zhong et al.', '2010', 'https://academic.oup.com/mbe/article/27/12/2855/1074835?login=true', 'Chloroplast', 'Chloroplast matrix'),
    ('DEN', 'Le Kim et al.', '2018', 'https://ieeexplore.ieee.org/abstract/document/8573341', 'Viral', 'Dengue Viruses'),
    ('Flavi', 'Le and Vinh', '2020', 'https://link.springer.com/article/10.1007/s00239-020-09943-3', 'Viral', 'Flavivirus'),
    ('Flu', 'Dang et al.', '2010', 'https://bmcecolevol.biomedcentral.com/articles/10.1186/1471-2148-10-99', 'Viral', 'Influenza virus'),
    ('gcpREV', 'Cox and Foster', '2013', 'https://www.sciencedirect.com/science/article/pii/S1055790313001395','Chloroplast', 'Chloroplast matrix'),
    ('HIVb', 'Nickle et al.', '2007', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0000503', 'Viral', 'HIV between-patient matrix HIV-Bm'),
    ('HIVw', 'Nickle et al.', '2007', 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0000503', 'Viral', 'HIV within-patient matrix HIV-Wm'),
    ('HIVin', 'del Amparo and Arenas', '2021', 'https://www.mdpi.com/2073-4425/13/1/61', 'Viral', 'HIV integrase matrix'),
    ('HIVpr','del Amparo and Arenas', '2021', 'https://www.mdpi.com/2073-4425/13/1/61', 'Viral', 'HIV protease matrix'),
    ('mtInv', 'Vinh et al.', '2017', 'https://link.springer.com/article/10.1186/s12862-017-0987-y', 'Mitochondrial', 'Mitochondrial Invertebrates'),
    ('mtMet', 'Vinh et al.', '2017', 'https://link.springer.com/article/10.1186/s12862-017-0987-y', 'Mitochondrial', 'Mitochondrial Metazoa'),
    ('mtVer', 'Vinh et al.', '2017', 'https://link.springer.com/article/10.1186/s12862-017-0987-y', 'Mitochondrial', 'Mitochondrial Vertebrates'),
    ('mtOrt', 'Chang et al.', '2020', 'https://link.springer.com/article/10.1186/s12862-020-01623-6', 'Mitochondrial', 'Mitochondrial Orthoptera Insects'),
    ('PMB', 'Veerassamy, et al.', '2003', 'https://www.liebertpub.com/doi/abs/10.1089/106652703322756195', 'Nuclear/General', 'Blocks Substitution Matrix'),
    ('QBird', 'Jarvis et al.', '2015', 'https://academic.oup.com/gigascience/article/4/1/s13742-014-0038-1/2707489?login=true', 'Nuclear', 'Q matrix estimated for birds'),
    ('QInsect', 'Misof et al.', '2014', 'https://academic.oup.com/gigascience/article/4/1/s13742-014-0038-1/2707489?login=true', 'Nuclear', 'Q matrix estimated for insects'),
    ('QLG', 'Minh et al.', '2021', 'https://academic.oup.com/sysbio/article/70/5/1046/6146362?login=true', 'Nuclear/General', 'Q matrix for LG'),
    ('QMammal', 'Wu et al.', '2018', 'https://www.sciencedirect.com/science/article/pii/S2352340918304475?via%3Dihub', 'Nuclear', 'Q matrix estimated for mammals'),
    ('QPfam', 'El-Gebali et al.', '2019', 'https://academic.oup.com/nar/article/47/D1/D427/5144153?login=true', 'Nuclear', 'General Q matrix estimated from Pfam version 31 database'),
    ('QPlant', 'Ran et al.', '2018', 'https://royalsocietypublishing.org/doi/10.1098/rspb.2018.1012', 'Nuclear', 'Q matrix estimated for plants'),
    ('QYeast', 'Shen et al.', '2018', 'https://www.sciencedirect.com/science/article/pii/S0092867418313321?via%3Dihub', 'Nuclear', 'Q matrix estimated for yeats'),
    ('rtREV', 'Dimmic et al.', '2002', 'https://link.springer.com/article/10.1007/s00239-001-2304-y', 'Viral', 'Retrovirus'),
    ('VT', 'Müller and Vingron', '2000', 'https://www.liebertpub.com/doi/abs/10.1089/10665270050514918', 'Nuclear', 'General Variable Time matrix'),
    ('AB', 'Mirsky et al.', '2015', 'https://academic.oup.com/mbe/article/32/3/806/980410?login=true', 'Antibody', 'Antibody-Specific Matrix'),
    ('stmtREV', 'Liu et al.', '2014', 'https://academic.oup.com/sysbio/article/63/6/862/2847701?login=true', 'Mitochondrial', 'Mitochondrial Plants'),
    ('BLOSUM62', 'Henikoff and Henikoff', '1992', 'https://www.pnas.org/doi/epdf/10.1073/pnas.89.22.10915', 'General', 'Blocks Substitution Matrix')
]

# Directory containing the substitution matrix files
data_dir = 'data'

# Create tables
create_tables()

# Insert model data into the database
insert_models(models)

# Insert substitution matrices into the database
insert_matrices(data_dir)
