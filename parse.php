<?php
/***
 * Projekt : IPP projekt, časť č.1 (Parser PHP 8.1)
 * @file parse.php
 * @author Kristián Kičinka (xkicin02)
 */


ini_set('display_errors','stderr');

// Definícia návratových kódov chybových hlášok.
const HEAD_ERROR = 21;
const ARG_ERROR = 10;
const OP_CODE_ERROR = 22;
const OTHER_ERROR = 23;

// Definícia konštánt na rozoznanie potrebných typov inštrukcií.
const VAR_ONLY = ["DEFVAR","POPS"];
const VAR_SYMBOL = ["MOVE","INT2CHAR","STRLEN","TYPE","NOT"];
const VAR_TYPE = ["READ"];
const VAR_SYM_SYM = ["ADD","SUB","MUL","IDIV","LT","GT","EQ","AND","OR","STRI2INT","CONCAT","GETCHAR","SETCHAR"];
const NO_PARAM = ["CREATEFRAME","PUSHFRAME","POPFRAME","RETURN","BREAK"];
const LABEL_ONLY = ["CALL","LABEL","JUMP"];
const SYMBOL_ONLY = ["PUSHS","WRITE","EXIT","DPRINT"];
const LABEL_SYM_SYM = ["JUMPIFEQ","JUMPIFNEQ"];

main($argc,$argv);

// Hlavná funkcia
function main($argc,$argv){
    check_arguments($argc,$argv);
    read_from_stdin();
}

/**
 * @brief Funkcia zabezpečuje kontrolu argumentov skriptu.
 * @param $argc - Počet argumentov
 * @param $argv - Pole argumentov
 * @return void
 */
function check_arguments($argc,$argv){
    if ($argc > 1){
        if ($argv[1] == "--help"){
            echo "Použitie :\n";
            echo "  parse.php --help            => Popis ovládania programu.\n";
            echo "  parse.php                   => Spustenie programu so štandardným vstupom.\n";
            echo "  parse.php < [input file]    => Spustenie programu so vstupným súborom.\n";
            exit(0);
        }else{
            return_error(ARG_ERROR);
        }
    }
}

/**
 * @brief Funkcia zabezpečuje kontrolu hlavičky vstupného kódu.
 * @param $line - Načítaný riadok zo vstupného súboru
 * @return bool
 */
function check_header($line): bool{
    global $header_count;
    if (trim($line) != ".IPPcode22") {
        if($header_count == 0)
            return false;
        return true;
    }else{
        if($header_count == 0){
            $header_count++;
            return true;
        }
        return_error(OP_CODE_ERROR);
        return false;
    }
}

/**
 * @brief Funkcia zabezpečuje čítanie vstupného súboru.
 * @return void
 */
function read_from_stdin(){
    $program_out = new ProgramOutput();
    $program_out->create_header();
    $inst_object = new Instruction();
    while ($line = fgets(STDIN)){
        $line = delete_comments($line);
        $header_correct = check_header($line);
        $commands = explode(' ',$line);
        check_command(array_values(array_filter($commands)),$program_out,$inst_object,$header_correct);
    }

    $program_out->create_end();
    $program_out->print_output();
}

/**
 * @brief Funkcia zabezpečuje vymazanie komentárov zo vstupného súboru.
 * @param $source - Riadok prečítaný zo vstupného súboru
 * @return array|mixed|string|string[]
 */
function delete_comments($source){
    $split = explode("#",$source,2);

    if(count($split)>1){
        $to_delete = "#".$split[1];
        $source = str_replace($to_delete,"",$source);
    }
    return $source;
}

/**
 * @brief Funkcia zabezpečuje overenie správnosti elementu variable.
 * @param $variable - Hodnota elementu variable
 * @return void
 */
function check_variable($variable){
    $regex = "'^(LF|GF|TF)@([_\-$&*!%?]|[a-z]|[A-Z])([_\-$&*!?%]|[a-z]|[A-Z]|[0-9]|\p{Latin})*'";
    $variable = trim($variable);
    if(!preg_match($regex,$variable)){
        return_error(OTHER_ERROR);
    }
}

/**
 * @brief Funkcia zabezpečuje overenie správnosti elementu symbol.
 * @param $symbol - Hodnota elementu symbol
 * @return void
 */
function check_symbol($symbol){
    $regex_constant_string = '/^(string)@([_\-><\/$&*!%?@]|[a-z]|[A-Z]|[\pL\pS\p{Pe},;§]|(\\\\\d{3}))?([_\-><\/$&*!%?@]|[a-z]|[A-Z]|[\pL\pS\p{Pe},;§]|\d|(\\\\\d{3}))*$/um';
    $regex_variable = "'^(LF|GF|TF)@([_\-$&*!%?]|[a-z]|[A-Z])([_\-$&*!?%]|[a-z]|[A-Z]|[0-9]|\p{Latin})*'";
    $regex_constant_nil = "'^(nil)@(nil)$'";
    $regex_constant_bool = "'^(bool)@(true|false)$'";
    $regex_constant_int = "'^(int)@([+-])?([0-9])+$'";
    $symbol = trim($symbol);

    if(!(preg_match_all($regex_constant_string,$symbol) || preg_match($regex_variable,$symbol) ||
        preg_match($regex_constant_nil,$symbol) || preg_match($regex_constant_bool,$symbol) ||
        preg_match($regex_constant_int,$symbol))){
        return_error(OTHER_ERROR);
    }
}

/**
 * @brief Funkcia zabezpečuje overenie správnosti elementu label.
 * @param $label - Hodnota elementu label
 * @return void
 */
function check_label($label){
    $regex = "'^([_\-$&*!%?]|[a-z]|[A-Z])([_\-$&*!?%]|[a-z]|[A-Z]|[0-9])*$'";
    $label = trim($label);
    if(!preg_match($regex,$label)){
        return_error(OTHER_ERROR);
    }
}

/**
 * @brief Funkcia zabezpečuje overenie správnosti elementu type.
 * @param $type - Hodnota elementu type
 * @return void
 */
function check_type($type){
    $regex = "'^(int|bool|string|nil|type|var)$'";
    $type = trim($type);
    if(!preg_match($regex,$type)){
        return_error(OTHER_ERROR);
    }
}

/**
 * @brief Funkcia zabezpečuje zápis elementu instruction na výstup programu.
 * @param $instruction - Hodnota elementu instruction
 * @param ProgramOutput $programOutput - Objekt výstupu programu
 * @param Instruction $inst_object - Objekt inštrukcie
 * @return void
 */
function print_instruction($instruction,ProgramOutput $programOutput, Instruction $inst_object){
    $inst_object->setOpcode($instruction);
    $programOutput->add_to_output($inst_object->create_instruction());
    $inst_object->increase_instruction_number();
}

/***
 * @brief Funkcia zabezpečuje zápis elementu symbol na výstup programu.
 * @param $symbol - Hodnota elementu symbol
 * @param Argument $argument - Objekt argumentu
 * @param ProgramOutput $programOutput - Objekt výstupu programu
 * @return void
 */
function print_symbol($symbol, Argument $argument,ProgramOutput $programOutput){
    $parsed_arg = explode('@',$symbol,2);
    $first_arg = trim($parsed_arg[0]);
    if($first_arg == "GF" || $first_arg =="LF" || $first_arg =="TF"){
        $argument->setType("var");
        $argument->setValue($symbol);
    }else{
        $argument->setType($parsed_arg[0]);
        $argument->setValue($parsed_arg[1]);
    }
    $programOutput->add_to_output($argument->create_argument());
    $argument->increase_arg_number();
}

/***
 * @brief Funkcia zabezpečuje zápis elementu variable na výstup programu.
 * @param $variable - Hodnota elementu variable
 * @param Argument $argument - Objekt argumentu
 * @param ProgramOutput $programOutput - Objekt výstupu programu
 * @return void
 */
function print_variable($variable,Argument $argument,ProgramOutput $programOutput){
    $argument->setType("var");
    $argument->setValue($variable);
    $programOutput->add_to_output($argument->create_argument());
    $argument->increase_arg_number();
}

/***
 * @brief Funkcia zabezpečuje zápis elementu label na výstup programu.
 * @param $label - Hodnota elementu label
 * @param Argument $argument - Objekt argumentu
 * @param ProgramOutput $programOutput - Objekt výstupu programu
 * @return void
 */
function print_label($label,Argument $argument,ProgramOutput $programOutput){
    $argument->setType("label");
    $argument->setValue($label);
    $programOutput->add_to_output($argument->create_argument());
    $argument->increase_arg_number();
}

/***
 * @brief Funkcia zabezpečuje zápis elementu type na výstup programu.
 * @param $type - Hodnota elementu type
 * @param Argument $argument - Objekt argumentu
 * @param ProgramOutput $programOutput - Objekt výstupu programu.
 * @return void
 */
function print_type($type,Argument $argument,ProgramOutput $programOutput){
    $argument->setType("type");
    $argument->setValue($type);
    $programOutput->add_to_output($argument->create_argument());
    $argument->increase_arg_number();
}

/***
 * @brief Funkcia zabezpečuje rozlýšenie inštrukcie a spravny postup jej spracovania.
 * @param $commands - Príkaz zo vstupu, ktorý ma byť spracovaný.
 * @param ProgramOutput $programOutput - Objekt výstupu programu.
 * @param Instruction $inst_object - Objekt inštrukcie.
 * @param $header - Premenná zabezpečujúca informáciu o stave hlavičky programu.
 * @return void
 */
function check_command($commands, ProgramOutput $programOutput, Instruction $inst_object,$header){
    if(count($commands)>=1 && trim($commands[0]) != ".IPPcode22" && trim($commands[0])!=""){
        if($header == false){
            return_error(HEAD_ERROR);
        }
        $params_count = count($commands)-1;
        $instruction = trim(strtoupper($commands[0]));
        $argument = new Argument();
        print_instruction($instruction,$programOutput,$inst_object);

        if(in_array($instruction,VAR_ONLY)){
            if($params_count == 1){
                check_variable(trim($commands[1]));
                print_variable(trim($commands[1]),$argument,$programOutput);
            }else{
                return_error(OTHER_ERROR);
            }
        }elseif (in_array($instruction,VAR_SYMBOL)){
            if($params_count == 2){
                check_variable($commands[1]);
                print_variable(trim($commands[1]),$argument,$programOutput);
                check_symbol($commands[2]);
                print_symbol(trim($commands[2]),$argument,$programOutput);
            }else{
                return_error(OTHER_ERROR);
            }
        }elseif (in_array($instruction,VAR_TYPE)){
            if($params_count == 2){
                check_variable($commands[1]);
                print_variable(trim($commands[1]),$argument,$programOutput);
                check_type($commands[2]);
                print_type(trim($commands[2]),$argument,$programOutput);
            }else{
                return_error(OTHER_ERROR);
            }
        }elseif (in_array($instruction,VAR_SYM_SYM)){
            if($params_count == 3){
                check_variable($commands[1]);
                print_variable(trim($commands[1]),$argument,$programOutput);
                check_symbol($commands[2]);
                print_symbol(trim($commands[2]),$argument,$programOutput);
                check_symbol($commands[3]);
                print_symbol(trim($commands[3]),$argument,$programOutput);
            }else{
                return_error(OTHER_ERROR);
            }
        }elseif (in_array($instruction,LABEL_ONLY)){
            if($params_count == 1){
                check_label($commands[1]);
                print_label(trim($commands[1]),$argument,$programOutput);
            }else{
                return_error(OTHER_ERROR);
            }
        }elseif (in_array($instruction,SYMBOL_ONLY)){
            if($params_count == 1){
                check_symbol($commands[1]);
                print_symbol(trim($commands[1]),$argument,$programOutput);
            }else{
                return_error(OTHER_ERROR);
            }
        }elseif (in_array($instruction,LABEL_SYM_SYM)){
            if($params_count == 3){
                check_label($commands[1]);
                print_label(trim($commands[1]),$argument,$programOutput);
                check_symbol($commands[2]);
                print_symbol(trim($commands[2]),$argument,$programOutput);
                check_symbol($commands[3]);
                print_symbol(trim($commands[3]),$argument,$programOutput);
            }else{
                return_error(OTHER_ERROR);
            }
        }elseif (in_array($instruction,NO_PARAM)){
            if ($params_count == 0){
                return;
            }else{
                return_error(OTHER_ERROR);
            }
        }else{
            return_error(OP_CODE_ERROR);
        }
        $programOutput->add_to_output($inst_object->create_end());
    }
}

// Triedy objektov

class Instruction{
    public int $instruction_number;
    public string $opcode;

    function __construct() {
        $this->instruction_number = 1;
        $this->opcode = "";
    }

    public function setOpcode($opcode)
    {
        $this->opcode = $opcode;
    }

    function increase_instruction_number(){
        $this->instruction_number++;
    }

    function create_instruction(): string{
        if(in_array($this->opcode,NO_PARAM)){
            return "\t<instruction order=\"$this->instruction_number\" opcode=\"$this->opcode\" />\n";
        }else{
            return "\t<instruction order=\"$this->instruction_number\" opcode=\"$this->opcode\">\n";
        }

    }

    function create_end(): string{
        return "\t</instruction>\n";
    }

}

class Argument{
    public int $argument_number;
    public string $type;
    public string $value;

    function __construct(){
        $this->argument_number = 1;
        $this->type = "";
        $this->value = "";
    }

    public function setType($type){
        $this->type = $type;
    }

    public function setValue($value){
        $this->value = $value;
    }

    public function increase_arg_number(){
        $this->argument_number++;
    }

    public function create_argument(): string{
        $this->value = str_replace("&","&amp;",$this->value);
        $this->value = str_replace(">","&gt;",$this->value);
        $this->value = str_replace("<","&lt;",$this->value);
        return "\t\t<arg$this->argument_number type=\"$this->type\">$this->value</arg$this->argument_number>\n";
    }
}

class ProgramOutput{
    public string $output;

    function __construct() {
        $this->output = "";
    }

    function create_header(){
        $this->output = $this->output."<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
        $this->output = $this->output."<program language=\"IPPcode22\">\n";
    }

    function create_end(){
        $this->output = $this->output."</program>\n";
    }

    function add_to_output($string){
        $this->output = $this->output.$string;
    }

    function print_output(){
        echo $this->output;
    }

}

/***
 * @brief Funkcia vráti patričnú chybovú hlášku a ukončí program.
 * @param $error - typ chybovej hlášky.
 * @return void
 */
function return_error($error){
    switch ($error){
        case HEAD_ERROR:
            fwrite(STDERR, "Chyba v hlavičke súboru!" . PHP_EOL);
            exit(HEAD_ERROR);
        case OP_CODE_ERROR:
            fwrite(STDERR, "Chyba operačného kódu!" . PHP_EOL);
            exit(OP_CODE_ERROR);
        case OTHER_ERROR:
            fwrite(STDERR, "Iná lexikálna alebo syntaktická chyba!" . PHP_EOL);
            exit(OTHER_ERROR);
        case ARG_ERROR:
            fwrite(STDERR, "Chyba vstupných argumentov skriptu!" . PHP_EOL);
            exit(ARG_ERROR);
    }
}