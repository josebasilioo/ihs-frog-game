
module pcihellocore (
	pcie_hard_ip_0_rx_in_rx_datain_0,
	pcie_hard_ip_0_tx_out_tx_dataout_0,
	pcie_hard_ip_0_powerdown_pll_powerdown,
	pcie_hard_ip_0_powerdown_gxb_powerdown,
	pcie_hard_ip_0_refclk_export,
	pcie_hard_ip_0_pcie_rstn_export,
	hexport_external_connection_export,
	inport_external_connection_export,
	hexport_left_external_connection_export,
	ex_green_led_external_connection_export,
	ex_red_led_external_connection_export,
	in_bottoms_external_connection_export);	

	input		pcie_hard_ip_0_rx_in_rx_datain_0;
	output		pcie_hard_ip_0_tx_out_tx_dataout_0;
	input		pcie_hard_ip_0_powerdown_pll_powerdown;
	input		pcie_hard_ip_0_powerdown_gxb_powerdown;
	input		pcie_hard_ip_0_refclk_export;
	input		pcie_hard_ip_0_pcie_rstn_export;
	output	[31:0]	hexport_external_connection_export;
	input	[15:0]	inport_external_connection_export;
	output	[31:0]	hexport_left_external_connection_export;
	output	[31:0]	ex_green_led_external_connection_export;
	output	[31:0]	ex_red_led_external_connection_export;
	input	[31:0]	in_bottoms_external_connection_export;
endmodule
