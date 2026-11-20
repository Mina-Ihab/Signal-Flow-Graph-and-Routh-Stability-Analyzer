from result import result
import math 
class routh:
    # i assumed that the coffs are ordered from the highest power to the lowest
    def __init__(self,coffs):
        self.result=result(coffs)
        self.coffs=coffs

    # quick sign check returns wehter to proceed forward or not
    def check_system(self):
        n=0
        for coff in self.coffs:
            if coff < 0:
                n+=1
        if n==len(self.coffs):
            self.coffs = [x * -1 for x in self.coffs]
            self.result.update_coffs(self.coffs)# updating the previous coffs if anyone accessed them from the reuslt class
            return True
        elif n >0 and n!=len(self.coffs):
            self.result.stability=False
            self.result.note="the system isnt stable as some coffs are negative, no point in calculating the routh table"
            return False
        else :
            return True

    @staticmethod
    def pad_wth_zeros(row, lenght):
        while len(row)< lenght:
            row.append(0)



   
    def calc(self):
        if not self.check_system():
            return self.result
        n=len(self.coffs)
        current_row=[]
        prev_upper_row=[]
        prev_lower_row=[]

        if n<2:
            if n==0:
                self.result.note="no thing here "
                self.result.stability=False
                return result
            else:
                self.result.table=[[self.coffs[0]],[0]]
                self.result.stability=True
                self.result.note="marginally stable"
                return result
            

        #building the first 2 rows
        turn=0 
        for coff in self.coffs:
            if turn %2 ==0:
                prev_upper_row.append(coff)
            else:
                prev_lower_row.append(coff)
            turn+=1
        #padding to avoid errors due to out of bound

        self.pad_wth_zeros(prev_upper_row,math.ceil(n/2))
        self.pad_wth_zeros(prev_lower_row,math.ceil(n/2))
        self.result.add_row(prev_upper_row)
        self.result.add_row(prev_lower_row)
        #build table
        for j in range(2,n):
            #build current row
            for i in range(math.ceil(n/2)-1):
                a11=prev_upper_row[0]
                a12=prev_upper_row[i+1]
                a21=prev_lower_row[0]
                a22=prev_lower_row[i+1]
                column=i
                row=j
                step=(a11,a12,a21,a22,i,j)
                self.result.add_step(step)
                try:
                    term=-(a11*a22-a21*a12)/a21
                    current_row.append(term)


                except ZeroDivisionError:
                    self.result.note="a zero was found in the first column "
                    self.result.stability=False
                    return self.result
            self.pad_wth_zeros(current_row,math.ceil(n/2))
            self.result.add_row(current_row)
            prev_upper_row=prev_lower_row
            prev_lower_row=current_row
            current_row=[]


        self.result.finished()
        return self.result
                




        
        


        
                
        
      
