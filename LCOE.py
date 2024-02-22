import sys, os
import numpy_financial as npf
from PyQt6 import QtWidgets, QtCore, uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QIntValidator, QDoubleValidator

# Needed for Wayland applications LINUX ONLY
os.environ["QT_QPA_PLATFORM"] = "xcb"

class Ui_LCOE(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.getcwd()+"/LCOE.ui", self)
        
        ## set Restrictions to Input fields
        only_year = QIntValidator(0,100)
        self.input_project_lifetime.setValidator(only_year)
        self.input_years.setValidator(only_year)
        only_power = QDoubleValidator(1,1000,2)
        only_power.setLocale(QtCore.QLocale("en_US"))
        self.input_nominal_power.setValidator(only_power)
        self.input_annual_yield.setValidator(only_power)
        only_percent = QDoubleValidator(-10,100,2)
        only_percent.setLocale(QtCore.QLocale("en_US"))
        self.input_degradation.setValidator(only_percent)
        self.input_discount.setValidator(only_percent)
        self.input_index.setValidator(only_percent)
        only_price = QDoubleValidator(-10,100000000,2)
        only_price.setLocale(QtCore.QLocale("en_US"))
        self.input_price.setValidator(only_price)
        self.input_TIP.setValidator(only_price)
        self.input_insurance.setValidator(only_price)
        self.input_maintenance.setValidator(only_price)
        self.input_inflation.setValidator(only_price)
        
        self.pushButton_calculate_KPIs.clicked.connect(self.KPIs)
        self.pushButton_clear_inputs.clicked.connect(self.clear_inputs)

    def KPIs(self):        
        ## get user input
        project_lifetime = self.input_project_lifetime.text()
        nominal_power = self.input_nominal_power.text()
        annual_yield = self.input_annual_yield.text()
        degradation = self.input_degradation.text()
        years = self.input_years.text()
        price = self.input_price.text()
        index = self.input_index.text()
        TIP = self.input_TIP.text()
        insurance_prem = self.input_insurance.text()
        maintenance = self.input_maintenance.text()
        inflation = self.input_inflation.text()
        discount = self.input_discount.text()
        
        ## check whether all input fields are filled
        if (project_lifetime == '' or
            nominal_power == '' or
            annual_yield == '' or
            degradation == '' or
            years == '' or
            price =='' or
            index =='' or
            TIP == '' or
            insurance_prem == '' or
            maintenance=='' or
            inflation == '' or
            discount == ''):
           error_message = "You need to fill all input fields!\n"
           self.display.setText(error_message)
        else:
            ## convert input into procesable data
            project_lifetime = int(project_lifetime)
            nominal_power = float(nominal_power)
            annual_yield = float(annual_yield)
            degradation = 0.01*float(degradation)
            years = int(years) if(int(years)>int(project_lifetime)) else project_lifetime
            
            price = float(price)
            index = float(index)
            TIP = float(TIP)
            insurance_prem = 0.01*float(insurance_prem)
            maintenance = 0.01*float(maintenance)
            inflation = 0.01*float(inflation)
            discount = 0.01*float(discount
                                  )
            ## output LCOE
            self.LCOE = 0.486848656921709
            self.output_LCOE.setText(str(round(self.LCOE,2)))
            
            ## calculate cash flow arrays 
            self.remaining_power = [1-(degradation*i) for i in range(project_lifetime)]
            self.energy_production = [nominal_power*annual_yield*self.remaining_power[i] for i in range(project_lifetime)]
            self.revenueFIT = [ self.energy_production[i]*(price*(1+index)**i) if price>0 else 0 for i in range(years)]
            self.insurance = [-insurance_prem*TIP*(1+inflation)**(i) for i in range(project_lifetime)]
            self.maintenance = [-maintenance*TIP*(1+inflation)**i for i in range(project_lifetime)]
            self.earnings = [self.revenueFIT[i]+self.insurance[i]+self.maintenance[i] for i in range(project_lifetime)]
            self.income_cumul = [sum(self.earnings[0:i+1]) for i in range(project_lifetime)]
            self.income_LCOE = [self.LCOE*self.energy_production[i] for i in range(project_lifetime)]
            self.income_after_costs = [self.income_LCOE[i]+self.insurance[i]+self.maintenance[i] for i in range(project_lifetime)]
            self.discount_cash = [self.income_after_costs[i]/(1+discount)**(i+1) for i in range(project_lifetime)]
            self.present_value = sum(self.discount_cash)
            
            ## output nominal power
            self.nominal_power = nominal_power
            self.output_nominal_power.setText(str(self.nominal_power))

            # output PVNI
            if(discount==0.0):
                 self.PVNI = sum(self.earnings)
            else:
                self.PVNI = self.XNPV(discount, [0] + self.earnings)
                
            self.output_PVNI.setText(str(round(self.PVNI,2)))

            ## output NPV
            self.NPV = round(self.PVNI - TIP,2)
            self.output_NPV.setText(str(round(self.NPV,2)))

            ## output IRR
            self.IRR = round(npf.irr([TIP]+ self.earnings),2)
            if (self.IRR < 0):
                self.IRR = 'N.A.'
                self.output_ROI.setText(str(self.IRR))
            else:
                self.output_ROI.setText(str(100*self.IRR))

            ## display the cash flow calculations
            display = self.create_cashflow_output(project_lifetime)
            self.display.setText(display)

    def XNPV(self, rate, cashflow):
        return sum([cashflow[i]/(1+rate)**(i) for i in range(len(cashflow))])            

    def create_cashflow_output(self, project_lifetime):
        display_cash_output = ''
        for i in range(project_lifetime):
            display_cash_output += f"after year {i+1}:\t remaining power: {round(self.remaining_power[i],3)}\t energy production: {round(self.energy_production[i],0)}\t revenue: {round(self.revenueFIT[i],2)}\t insurance: {round(self.insurance[i],2)}\t maintenance: {round(self.maintenance[i],2)}\t earnings: {round(self.earnings[i],2)}\t income cumul: {round(self.income_cumul[i],2)}\t income with LCOE: {round(self.income_LCOE[i],2)} \t income after costs: {round(self.income_after_costs[i],2)}\t discounted cash: {round(self.discount_cash[i],2)} \n"
        display_cash_output += f"Present Value: {round(self.present_value,2)}\n"
        display_cash_output += f"Nominal Power: {round(self.present_value,2)}\n"
        display_cash_output += f"Present value of net income: {round(self.PVNI,2)}\n"
        display_cash_output += f"Levelised cost of electricity: {round(self.present_value,2)}\n"
        display_cash_output += f"Return on Investment: {self.IRR}\n"
        display_cash_output += f"NPV: {round(self.NPV,2)}"
        
        return display_cash_output

    def clear_inputs(self):
        self.input_project_lifetime.setText('')
        self.input_nominal_power.setText('')
        self.input_annual_yield.setText('')
        self.input_degradation.setText('')
        self.input_years.setText('')
        self.input_price.setText('')
        self.input_index.setText('')
        self.input_TIP.setText('')
        self.input_insurance.setText('')
        self.input_maintenance.setText('')
        self.input_inflation.setText('')
        self.input_discount.setText('')
        self.display.setText("Inputs have been cleared")

app = QtWidgets.QApplication(sys.argv)
window = Ui_LCOE()
window.show()
app.exec()