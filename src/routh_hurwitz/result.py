import numpy as np 

class result:


    

    def __init__(self, coffs):
        self.coffs = coffs
        self.poles = np.roots(coffs)
        self.steps = []
        self.table = []
        self.stability = False
        self.num_right_poles = None
        self.note = ""

    def add_step(self,step):
        self.steps.append(step)
    def add_row(self,row):
        self.table.append(row)
    def update_coffs(self,new_coffs):
        self.coffs=new_coffs
        self.poles = np.roots(new_coffs)

    def finished(self):
        self.stability=True
        self.num_right_poles=0
        prev=1

        for i in range(len(self.table)):
            current=self.table[i][0]

            if current > 0:
                pass
            else:
                if i==len(self.table)-1:

                    self.stability=True
                    self.note="marginally stable"
                else :
                    self.stability=False

            if prev*current<0:
                self.num_right_poles+=1
            prev =current


