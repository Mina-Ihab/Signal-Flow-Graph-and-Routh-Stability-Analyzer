class RSC :  

    def __init__(self,equation:str):

        self.equation = self.parser(equation)    
 
    def parser(self,equation:str):

        result = []
        splitted = equation.split(" ")
    
        for i in splitted:
    
            if i == '+' or i == '-' :
                continue

            coff = 1.0
            power = 1

            if i.find("x") == -1:
                power = 0
                coff = float(i)

            else:
            
                if i.find("*x") != -1 :

                    coff = float(i.split("*x")[0])

                if i.find("x**") != -1 :

                    try:
                        power = int(i.split("x**")[1])
                    except:
                        raise ValueError("integer power only are vaild")
            
            result.append([coff,power])
        return result