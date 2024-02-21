import sys, os
from cryptography.fernet import Fernet
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QDialog, QFileDialog
from PyQt6.QtGui import QIntValidator, QDoubleValidator

# Needed for Wayland applications
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
        self.input_nominal_power.setValidator(only_power)
        self.input_annual_yield.setValidator(only_power)
        only_percent = QDoubleValidator(0,100,2)
        #self.input_degradation.setValidator(only_percent)
        self.input_discount.setValidator(only_percent)
        self.input_index.setValidator(only_percent)
        only_price = QDoubleValidator(-10,100000000,2)
        self.input_price.setValidator(only_price)
        self.input_TIP.setValidator(only_price)
        self.input_insurance.setValidator(only_price)
        self.input_maintenance.setValidator(only_price)
        self.input_inflation.setValidator(only_price)
        
        self.pushButton_Calculate_KPIs.clicked.connect(self.KPIs)

    def KPIs(self):
        error_string = ''
        project_lifetime = int(self.input_project_lifetime.text())
        nominal_power = float(self.input_nominal_power.text())
        annual_yield = float(self.input_annual_yield.text())
        degradation = 0.01*float(self.input_degradation.text())
        years = int(self.input_years.text())
        price = float(self.input_price.text())
        index = float(self.input_index.text())
        TIP = float(self.input_TIP.text())
        insurance_prem = 0.01*float(self.input_insurance.text())
        maintenance = 0.01*float(self.input_maintenance.text())
        inflation = 0.01*float(self.input_inflation.text())
        discount = 0.01*float(self.input_discount.text())
        ## check whether all input fields are filled
        if False: pass#(project_lifetime == '' or
        #     nominal_power == '' or
        #     annual_yield == '' or
        #     degradation == '' or
        #     years == '' or
        #     price =='' or
        #     index =='' or
        #     TIP == '' or
        #     insurance_prem == '' or
        #     maintenance=='' or
        #     inflation == '' or
        #     discount == ''):
        #    error_string += "You need to fill all input fields!\n"
        #    self.display.setText(error_string)
        else:
            display = ''
            self.remaining_power = [1-(degradation*i) for i in range(project_lifetime)]
            self.energy_production = [nominal_power*annual_yield*self.remaining_power[i] for i in range(project_lifetime)]
            self.revenueFIT = [ self.energy_production[i]*(price*(1+index)**i) if price>0 else 0 for i in range(years)]
            self.insurance = [-insurance_prem*TIP*(1+inflation)**(i) for i in range(project_lifetime)]
            self.maintenance = [-maintenance*TIP*(1+inflation)**i for i in range(project_lifetime)]
            self.earnings = [self.revenueFIT[i]+self.insurance[i]+self.maintenance[i] for i in range(project_lifetime)]
            self.income_cumul = [sum(self.earnings[0:i+1]) for i in range(project_lifetime)]
            self.output_LCOE.setText(str(0.486848656921709))
            self.LCOE = float(self.output_LCOE.text())
            self.income_LCOE = [self.LCOE*self.energy_production[i] for i in range(project_lifetime)]
            self.income_after_costs = [self.income_LCOE[i]+self.insurance[i]+self.maintenance[i] for i in range(project_lifetime)]
            self.discount_cash = [self.income_after_costs[i]/(1+discount)**(i+1) for i in range(project_lifetime)]
            for i in range(project_lifetime):
                display += f"after year {i+1}:\t remaining power: {round(self.remaining_power[i],3)}\t energy production: {round(self.energy_production[i],0)}\t revenue: {round(self.revenueFIT[i],2)}\t insurance: {round(self.insurance[i],2)}\t maintenance: {round(self.maintenance[i],2)}\t earnings: {round(self.earnings[i],2)}\t income cumul: {round(self.income_cumul[i],2)}\t income with LCOE: {round(self.income_LCOE[i],2)} \t income after costs: {round(self.income_after_costs[i],2)}\t discounted cash: {round(self.discount_cash[i],2)} \n"
            self.display.setText(display)
app = QtWidgets.QApplication(sys.argv)
window = Ui_LCOE()
window.show()
app.exec()