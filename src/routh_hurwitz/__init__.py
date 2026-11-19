class RSC :  

    def __init__(self,equation:str):

        self.coffs , self.powers = self.parser(equation)    

 
    def parser(self,equation:str):

        coffs = []
        powers = []
        splitted = equation.split(" ")
    
        for i in range(len(splitted) - 1, -1, -1):    
        
            if splitted[i] == '+' or splitted[i] == '-' :
                continue

            coff = 1.0
            power = 1

            if splitted[i].find("x") == -1:
                power = 0
                coff = float(i)

            else:
            
                if splitted[i].find("*x") != -1 :

                    coff = float(splitted[i].split("*x")[0])

                if splitted[i].find("x**") != -1 :

                    try:
                        power = int(splitted[i].split("x**")[1])
                    except:
                        raise ValueError("integer power only are vaild")

            coffs.append(coff)
            powers.append(power)

        return coffs,powers



e = RSC("-1*x**4 + -5*x**3 + 7*x")
