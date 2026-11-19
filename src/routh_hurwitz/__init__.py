class RSC :  

    def __init__(self,equation:str):

        self.coffs = self.parser(equation)    


    def parser(self,equation:str):

        coffs = []
        splitted = equation.split(" ")
        index = 0

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

            while index < power :
                coffs.append(0.0)
                index += 1
            index += 1

            coffs.append(coff)


        return coffs
