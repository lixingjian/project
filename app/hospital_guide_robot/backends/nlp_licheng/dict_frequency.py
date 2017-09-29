# -*- coding: utf-8 -*-

'''
Author: chenlee
'''
from Match import Match
import codecs

class Frequency:
    def __init__(self, file_dir):
        #add key to ahocorasick
        self.organ_match = Match()
        self.organ_match.load(os.path.join(file_dir,'organ_nlp'))

        self.tissue_match = Match()
        self.tissue_match.load(os.path.join(file_dir,'tissue_nlp'))

        self.indicator_match = Match()
        self.indicator_match.load(os.path.join(file_dir,'indicator_nlp'))
        
        self.function_match = Match()
        self.function_match.load(os.path.join(file_dir,'function_nlp'))
        
        self.nutrition_match = Match()
        self.nutrition_match.load(os.path.join(file_dir,'nutrition_nlp'))

        self.problem_match = Match()
        self.problem_match.load(os.path.join(file_dir,'problem_nlp'))

        self.appearance_match = Match()
        self.appearance_match.load(os.path.join(file_dir,'appearance_nlp'))

        #two dimention dict
        '''
            for example:
                {organ_name:{problem_name:frequency}}
        '''
        organ_dict = {}
        tissue_dict = {}
        indicator_dict = {}
        function_dict = {}
        nutrition_dict = {}


    def  
