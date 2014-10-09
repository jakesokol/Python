<?php
// This script will pull recent F2300 data collected from MySQL DB and format the info into tables to display info
// Author: Jake Sokol
// Version: 1.0


//AEI Page Header
require("session.php");
require("header.php"); 

//values for table
$serial_array=array();
$dut_array=array();
$firm_array=array();
$uptime_array=array();
$uptime_value_array=array();
$contact_time_array=array();
$cpu0_idle_array=array();
$cpu1_idle_array=array();
$cpu0_usr_array=array();
$cpu1_usr_array=array();
$cpu0_sys_array=array();
$cpu1_sys_array=array();
$cpu0_usage_array=array();
$cpu1_usage_array=array();
$mem_total_array=array();
$mem_avail_array=array();
$mem_free_array=array();
$mem_buffer_array=array();
$mem_cached_array=array();
$smem_total_array=array();
$smem_free_array=array();
$smem_inuse_array=array();
$smem_usable_array=array();
$conntrack_array=array();
$conntrack_value_array=array();
$alert_entries_array=array();
?>

<html><font face = "helvetica" >
<body></br>
	
	<?php

	//
	// Collect all data from and prepare values for graph and table
	//
	for ($i=1; $i < 7; $i++)
	{
		$result_basicinfo = mysql_query("SELECT * FROM uptime ORDER BY TIMESTAMP DESC LIMIT 1", $dbserver5);
		$result_cpu = mysql_query("SELECT * FROM cpu ORDER BY TIMESTAMP DESC LIMIT 1", $dbserver5);
		$result_mem = mysql_query("SELECT * FROM memory  ORDER BY TIMESTAMP DESC LIMIT 1", $dbserver5);
		$result_smem = mysql_query("SELECT * FROM smem ORDER BY TIMESTAMP DESC LIMIT 1",  $dbserver5);
		$result_conntrack = mysql_query("SELECT * FROM conntrack ORDER BY TIMESTAMP DESC LIMIT 1",  $dbserver5);
		$result_alerts = mysql_query("SELECT * FROM alerts",  $dbserver5);

		// pushing MSYQL results into array
		// If the values are empty, replace with "filler" values for the table
		// Data processing for basic info (DUT / SERIAL / SWVER / UPTIME)
		$result_num = mysql_num_rows($result_basicinfo);
		if ($result_num > 0){
			while ($row_basicinfo = mysql_fetch_array($result_basicinfo))
			{	
				array_push($dut_array, $row_basicinfo['DUT']);
				array_push($serial_array, $row_basicinfo['SERIAL']);
				array_push($firm_array, $row_basicinfo['SWVER']);
				array_push($uptime_array, $row_basicinfo['DATA']);
				array_push($contact_time_array, $row_basicinfo['TIMESTAMP']);
				
				// Converting uptime dates into int values(HR)
				$days = explode(" ",intval($row_basicinfo['DATA']));
				array_push($uptime_value_array, $days[0]);
			}
		}
		else{
			array_push($dut_array, "N/A");
			array_push($serial_array, "N/A");
			array_push($firm_array, "N/A");
			array_push($uptime_array, "N/A");
			array_push($uptime_value_array, 0);
			array_push($contact_time_array, "N/A");
		}
		
		// Data processing for CPU info
		$result_num = mysql_num_rows($result_cpu);
		if ($result_num > 0){		
			while ($row_cpu = mysql_fetch_array($result_cpu))
			{
				$cpu0_usage = 100-$row_cpu['CPU0_IDLE'];
				$cpu1_usage = 100-$row_cpu['CPU1_IDLE'];
				array_push($cpu0_usage_array, floatval($cpu0_usage));
				array_push($cpu1_usage_array, floatval($cpu1_usage));
				array_push($cpu0_idle_array, $row_cpu['CPU0_IDLE']);
				array_push($cpu1_idle_array, $row_cpu['CPU1_IDLE']);
				array_push($cpu0_usr_array, $row_cpu['CPU0_USR']);
				array_push($cpu1_usr_array, $row_cpu['CPU1_USR']);
				array_push($cpu0_sys_array, $row_cpu['CPU0_SYS']);
				array_push($cpu1_sys_array, $row_cpu['CPU1_SYS']);
			}
		}
		else {
			array_push($cpu0_usage_array, "N/A");
			array_push($cpu1_usage_array, "N/A");
			array_push($cpu0_idle_array, "N/A");
			array_push($cpu1_idle_array, "N/A");
			array_push($cpu0_usr_array, "N/A");
			array_push($cpu1_usr_array, "N/A");
			array_push($cpu0_sys_array, "N/A");
			array_push($cpu1_sys_array, "N/A");
		}

		// Data processing for MEMORY info
		$result_num = mysql_num_rows($result_mem);
		if ($result_num > 0){
			while ($row_mem = mysql_fetch_array($result_mem))
			{
				$total_mem = $row_mem['MEM_TOTAL'];
				$free_mem = $row_mem['MEM_FREE'];
				$buffer_mem = $row_mem['MEM_BUFFERS'];
				$cached_mem = $row_mem['MEM_CACHED'];
				$avail_mem = $row_mem['MEM_FREE']+$row_mem['MEM_BUFFERS']+$row_mem['MEM_CACHED'];
				array_push($mem_total_array, $total_mem);
				array_push($mem_free_array, $free_mem);
				array_push($mem_buffer_array, $buffer_mem);
				array_push($mem_cached_array, $cached_mem);
				array_push($mem_avail_array, $avail_mem);
			}
		}
		else {
			array_push($mem_total_array, "N/A");
			array_push($mem_free_array, "N/A");
			array_push($mem_buffer_array, "N/A");
			array_push($mem_cached_array, "N/A");
			array_push($mem_avail_array, "N/A");
		}

		//Data processing for SHARE MEMORY info
		$result_num = mysql_num_rows($result_smem);
		if ($result_num > 0){
			while ($row_smem = mysql_fetch_array($result_smem))
			{
				$total_smem = $row_smem['SMEM_TOTAL'];
				$free_smem = $row_smem['SMEM_FREE'];
				$inuse_smem = $row_smem['SMEM_INUSED'];
				$usable_smem = $row_smem['SMEM_USABLE'];
				array_push($smem_total_array, $total_smem);
				array_push($smem_free_array, $free_smem);
				array_push($smem_inuse_array, $inuse_smem);
				array_push($smem_usable_array, $usable_smem);
			}
		}
		else {
			array_push($smem_total_array, "N/A");
			array_push($smem_free_array, "N/A");
			array_push($smem_inuse_array, "N/A");
			array_push($smem_usable_array, "N/A");
		}
		
		// Data processing for CONNTRACK info
		$result_num = mysql_num_rows($result_conntrack);
		if ($result_num > 0){
			while ($row_conntrack = mysql_fetch_array($result_conntrack))
			{
				array_push($conntrack_array, $row_conntrack['DATA']);
				array_push($conntrack_value_array, $row_conntrack['DATA']);
			}
		}
		else {
			array_push($conntrack_array, "N/A");
			array_push($conntrack_value_array, 0);
		}
		
		// Alerts collected for each DUT
		$result_num = mysql_num_rows($result_alerts);
		array_push($alert_entries_array, $result_num);
		
	}
	// Close MySQL connection
	mysql_close();

	//
	// Display the Overview table 
	//
	echo "<dev>";
	echo "<table border='2' style='border-collapse:collapse; font-size:14px' cellpadding='2' align=center >";
	echo "<tr style='background-color:#4747A3'> <th colspan='13'><font color=#FFFFFF>F2300 Soak Station Overview</font></th></tr>";
	echo "<tr style='background-color:#91B5FF'> <th>UNIT</th> <th>DUT</th> <th>SERIAL</th> <th>FW VERSION</th> <th>UPTIME</th> <th>TRAFFIC(CT)</th> <th>LAST CONTACT</th> <th>ALERTS</th></tr>";
	for ($i=0; $i < 6; $i++)
	{	
		// Highlight role if:
		// 1. DUT entry is not available
		// 2. Uptime is less than 1 day
		$check_uptime = explode(" ", $uptime_array[$i]);
		if (($serial_array[$i] == "N/A") || (intval($check_uptime[0]) < 1)){
			$bgcolor ="#FF9175";}

		// Alternating row colors
		else {
			if ($i & 1){$bgcolor="#EFFFE1";}
			else {$bgcolor="#FFFFE1";}
		}
		
		// Display Unit + DUT + Serial
		echo "<tr style='background-color:$bgcolor'><td>";
		$row_num = $i + 1;
		echo "$row_num";
		echo "</td><td>";
		echo "$dut_array[$i]";
		echo "</td><td>";
		echo "$serial_array[$i]";
		echo "</td><td>";
	
		// Display Firmware version and uptime
		echo "$firm_array[$i]";
		echo "</td><td>";
		echo "$uptime_array[$i]";
		echo "</td><td>";
		
		// Display Conntrack (Traffic Load)
		echo "$conntrack_array[$i]";
		echo "</td><td>";
		
		// Display last contact time
		echo "$contact_time_array[$i]";
		echo "</td><td>";
		
		// Display number of alerts for each DUT
		echo "$alert_entries_array[$i]";
		echo "</td></tr>";
	}
	echo "</table>";
	echo "</dev>";
	?>
	<body></br>
	<?
	// Display the Memory table 
	//

	echo "<dev>";
	echo "<table border='2' style='border-collapse:collapse; font-size:14px' cellpadding='2' align=center >";
	echo "<tr style='background-color:#4747A3'> <th colspan='13'><font color=#FFFFFFF>Memory Usage</font></th></tr>";
	echo "<tr style='background-color:#91B5FF'> <th>UNIT</th> <th>SERIAL</th> <th>TOTAL MEM</th> <th>FREE MEM</th> <th>MEM BUFFERS</th> <th>MEM CACHED</th> <th>AVAILABLE MEM</th> </tr>";
	for ($i=0; $i < 6; $i++)
	{	
		// Highlight role if:
		// 1. DUT entry is not available
		// 2. Uptime is less than 1 day
		$check_uptime = explode(" ", $uptime_array[$i]);
		if (($serial_array[$i] == "N/A") || (intval($check_uptime[0]) < 1)){
			$bgcolor ="#FF9175";}

		// Alternating row colors
		else {
			if ($i & 1){$bgcolor="#EFFFE1";}
			else {$bgcolor="#FFFFE1";}
		}
		
		// Display Unit + DUT + Serial
		echo "<tr style='background-color:$bgcolor'><td>";
		$row_num = $i + 1;
		echo "$row_num";
		echo "</td><td>";
		echo "$serial_array[$i]";
		echo "</td><td>";

		// Display Memory Usage
		echo "$mem_total_array[$i]"; 
		echo "</td><td>";
		echo "$mem_free_array[$i]";
		echo "</td><td>";
		echo "$mem_buffer_array[$i]"; 
		echo "</td><td>";
		echo "$mem_cached_array[$i]"; 
		echo "</td><td>";
		echo "$mem_avail_array[$i]";
		echo "</td></tr>";
	}	
    echo "</table>";
	echo "</dev>";
	?>
	<body></br>
	<?
	// Display the SMemory table 
	//

	echo "<dev>";
	echo "<table border='2' style='border-collapse:collapse; font-size:14px' cellpadding='2' align=center >";
	echo "<tr style='background-color:#4747A3'> <th colspan='13'><font color=#FFFFFFF>Shared Memory</font></th></tr>";
	echo "<tr style='background-color:#91B5FF'> <th>UNIT</th> <th>SERIAL</th> <th>TOTAL SMEM</th> <th>FREE SMEM</th> <th>SMEM IN USE</th> <th>USABLE SMEM</th> </tr>";
	for ($i=0; $i < 6; $i++)
	{	
		// Highlight role if:
		// 1. DUT entry is not available
		// 2. Uptime is less than 1 day
		$check_uptime = explode(" ", $uptime_array[$i]);
		if (($serial_array[$i] == "N/A") || (intval($check_uptime[0]) < 1)){
			$bgcolor ="#FF9175";}

		// Alternating row colors
		else {
			if ($i & 1){$bgcolor="#EFFFE1";}
			else {$bgcolor="#FFFFE1";}
		}
		
		// Display Unit + DUT + Serial
		echo "<tr style='background-color:$bgcolor'><td>";
		$row_num = $i + 1;
		echo "$row_num";
		echo "</td><td>";
		echo "$serial_array[$i]";
		echo "</td><td>";

		// Display Shared Memory Usage
		echo "$smem_total_array[$i]"; 
		echo "</td><td>";
		echo "$smem_free_array[$i]";
		echo "</td><td>";
		echo "$smem_inuse_array[$i]"; 
		echo "</td><td>";
		echo "$smem_usable_array[$i]"; 
		echo "</td></tr>";
	}	
    echo "</table>";
	echo "</dev>";
	?>
	<body></br>
	<?
	
	// Display the CPU table 
	//
	echo "<dev>";
	echo "<table border='2' style='border-collapse:collapse; font-size:14px' cellpadding='2' align=center >";
	echo "<tr style='background-color:#4747A3'> <th colspan='13'><font color=#FFFFFF>CPU STATUS</font></th></tr>";
	echo "<tr style='background-color:#91B5FF'> <th>UNIT</th> <th>SERIAL</th> <th>CPU0 USR</th> <th>CPU1 USR</th> <th>CPU0 SYS</th> <th>CPU1 SYS</th> <th>CPU0 IDLE</th> <th>CPU1 IDLE</th> <th>CPU0 USAGE</th> <th>CPU1 USAGE</th> </tr>";
	
	for ($i=0; $i < 6; $i++)
	{	
		// Highlight role if:
		// 1. DUT entry is not available
		// 2. Uptime is less than 1 day
		$check_uptime = explode(" ", $uptime_array[$i]);
		if (($serial_array[$i] == "N/A") || (intval($check_uptime[0]) < 1)){
			$bgcolor ="#FF9175";}

		// Alternating row colors
		else {
			if ($i & 1){$bgcolor="#EFFFE1";}
			else {$bgcolor="#FFFFE1";}
		}
		
		// Display Unit + Serial
		echo "<tr style='background-color:$bgcolor'><td>";
		$row_num = $i + 1;
		echo "$row_num";
		echo "</td><td>";
		echo "$serial_array[$i]";
		echo "</td><td>";

		// Display CPU usage information
		echo "$cpu0_usr_array[$i]";
		echo "</td><td>";
		echo "$cpu1_usr_array[$i]";
		echo "</td><td>";
		echo "$cpu0_sys_array[$i]";
		echo "</td><td>";
		echo "$cpu1_sys_array[$i]";
		echo "</td><td>";
		echo "$cpu0_idle_array[$i]";
		echo "</td><td>";
		echo "$cpu1_idle_array[$i]";
		echo "</td><td>";
		echo "$cpu0_usage_array[$i]"; 
		echo "</td><td>";
		echo "$cpu1_usage_array[$i]";
		echo "</td></tr>";
	}
	
	echo "</table>";
	echo "</dev>";
	?>
</body>	
</font></html>
