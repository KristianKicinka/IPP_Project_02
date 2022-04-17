<?php

/***
 * Projekt : IPP projekt, časť č.2 (Test PHP 8.1)
 * @file test.php
 * @author Kristián Kičinka (xkicin02)
 */

use objects\Output;
use objects\Script;
use objects\TestObject;
use objects\TestProcess;

ini_set('display_errors','stderr');

require_once("testerFiles/objects/Script.php");
require_once("testerFiles/objects/TestObject.php");
require_once("testerFiles/objects/TestProcess.php");
require_once("testerFiles/objects/Output.php");

const ARG_ERROR = 10;
const FILE_ERROR = 41;
const FILE_SEPARATOR = "/";
const PHP_TAG = "php";
const PYTHON_TAG = "python3.8";

main($argc, $argv);

// Hlavná funkcia
function main($argc, $argv){
    $script = new Script();
    array_shift($argv);
    process_arguments($argc, $argv, $script);
    $tests = load_tests($script);
    process_extensions($tests);
    testing($tests, $script);
}

/**
 * @brief Funkcia zabezpečuje ukončenie skriptu s patričným návratovým kódom
 * @param $code - Návratový kód
 * @return void
 */
function close_script($code){
    switch ($code){
        case ARG_ERROR:
            echo "Arguments error!\n";
            break;
        case FILE_ERROR:
            echo "File error!\n";
            break;
    }
    exit($code);
}

/**
 * @brief Funkcia zabezpečuje spracovanie argumentov skriptu
 * @param $argc - Počet arbumentov
 * @param $argv - Argumeny
 * @param $script - Objekt združujúci informácie o python skripte
 * @return void
 */
function process_arguments($argc, $argv, $script){
    if ($argc > 1){
        foreach($argv as $arg){
            switch ($arg){
                case "--help":
                    echo "Help function\n";
                    exit(0);
                case (bool)preg_match("'^--directory=(.+)$'", $arg, $results):
                    $script->setDirectoryPath($results[1]);
                    break;
                case "--recursive":
                    $script->setRecursive(true);
                    break;
                case (bool)preg_match("'^--parse-script=(.+)$'", $arg, $results):
                    $script->setParseScriptFile($results[1]);
                    break;
                case (bool)preg_match("'^--int-script=(.+)$'", $arg, $results):
                    $script->setIntScriptFile($results[1]);
                    break;
                case "--parse-only":
                    $script->setIntTests(false);

                    break;
                case "--int-only":
                    $script->setParseTests(false);
                    break;
                case (bool)preg_match("'^--jexampath=(.+)$'", $arg, $results):
                    $script->setJexamPath($results[1]);
                    break;
                case "--noclean":
                    $script->setCleanFiles(false);
                    break;
                default :
                    close_script(ARG_ERROR);
            }
        }
    }else{
        close_script(ARG_ERROR);
    }
}


/**
 * @brief Funkcia zabezpečuje prehľadanie testovacieho adresára a uloženie zoznamu súborov
 * @param $directory_path - Cesta k testovaciemu adresáru
 * @param $script - Objekt združujúci informácie o python skripte
 * @return array
 */
function scan_directory($directory_path, $script): array {
    $files_list = [];

    $dir_content = scandir($directory_path);

    foreach ($dir_content as $item){

        if ($item == "." or $item == ".." or ""){
            continue;
        }

        $file_path = $directory_path.FILE_SEPARATOR.$item;

        if (is_dir($file_path) == true){
            if ($script->isRecursive() == true){
                // Rekurzívne volanie funkcie skenovania adresára a uloženie hodnôt do zoznamu
                array_push($files_list, ...scan_directory($file_path, $script));
            }
        }else{
            $files_list[] = pathinfo($file_path);
        }
    }
    return $files_list;
}

/**
 * @brief Funkcia zabezpečuje načítanie testovacích súborov a vytvorenie testovacích objektov
 * @param $script - Objekt združujúci informácie o python skripte
 * @return array
 */
function load_tests($script): array {

    $directory_path = $script->getDirectoryPath();
    $tests_list = [];
    $test_files_list = scan_directory($directory_path, $script);


    foreach ($test_files_list as $test_file){
        $name  = $test_file["filename"];
        $directory_path = $test_file["dirname"];
        $file_path = $directory_path.FILE_SEPARATOR.$name;
        $extension = $test_file["extension"];

        if (!in_array($extension,["src","in","out","rc"])){
            continue;
        }

        if (!array_key_exists($file_path, $tests_list)){
            $tests_list[$file_path] = new TestObject($name, $directory_path, $file_path);
        }

        switch ($extension){
            case "src":
                $tests_list[$file_path]->setSrcFile(true);
                break;
            case "in":
                $tests_list[$file_path]->setInFile(true);
                break;
            case "out":
                $tests_list[$file_path]->setOutFile(true);
                break;
            case "rc":
                $tests_list[$file_path]->setRcFile(true);
                break;
        }

    }

    return $tests_list;

}

/**
 * @brief Funkcia zabezpečuje spracovanie prípon súborov, generovanie chýbajúcich súborov
 * @param $tests - Zoznam testovacích objektov (testov)
 * @return void
 */
function process_extensions($tests){
    foreach ($tests as $test){

        if ($test->isSrcFile()){
            if (!$test->isInFile()){
                file_put_contents($test->getTestFilePath().".in",'');
            }
            if (!$test->isOutFile()){
                file_put_contents($test->getTestFilePath().".out",'');
            }
            if (!$test->isRcFile()){
                file_put_contents($test->getTestFilePath().".rc",'0');
            }
        }

    }
}

/**
 * @brief Funkcia zabezpečuje spracovanie návratových kódov
 * @param $test - Testovací objekt
 * @return bool|string
 */
function load_rc_number($test): bool|string {
    $rc_file = $test->getTestFilePath().".rc";
    return file_get_contents($rc_file);
}

/**
 * @brief Funkcia zabezpečuje spracovanie parse testov
 * @param $test - Testovací objekt
 * @param $script - Objekt združujúci informácie o python skripte
 * @return TestProcess
 */
function process_parse_test($test, $script): TestProcess
{
    $process_name = $test->getTestName();
    $process_type = "parse";

    $src_file = $test->getTestFilePath().".src";
    $out_file = $test->getTestFilePath().".tmp_parse_out";
    $err_file = $test->getTestFilePath().".tmp_parse_err";

    // Vytvorenie testovacieho procesu
    $test_process = new TestProcess($process_type, $process_name, $src_file);
    $test_process->setTmpErrFilePath($err_file);
    $test_process->setTmpOutFilePath($out_file);

    // Vytvorenie php príkazu pre parse.php
    $php_command = PHP_TAG." ".$script->getParseScriptFile()." <".$src_file." 2>".$err_file." 1>".$out_file;

    exec($php_command, $output, $returned_code);

    $test_process->setExpectedExitCode(load_rc_number($test));
    $test_process->setReturnedExitCode($returned_code);

    if ($returned_code != $test_process->getExpectedExitCode()){

        $test_process->setTestPassed(false);
        $script->incFailedTestCount();

        return $test_process;
    }

    // Vytvorenie a spustenie porovnávania výstupov pomocou probramu jexamxml
    $expected_out = $test->getTestFilePath().".out";
    $jexam_jar = $script->getJexamPath().FILE_SEPARATOR."jexamxml.jar";
    $jexam_options = $script->getJexamPath().FILE_SEPARATOR."options";
    $jexam_exec = "java -jar ".$jexam_jar." ".$out_file." ".$expected_out." diffs.xml  /D ".$jexam_options;

    exec($jexam_exec, $output, $returned_code_cmp);
    @unlink("diffs.xml");

    if ($returned_code_cmp != 0){
        $test_process->setTestPassed(false);
        $script->incFailedTestCount();
    }else{
        $test_process->setTestPassed(true);
        $script->incPassedTestCount();
    }

    return $test_process;
}

/**
 * @brief Funkcia zabezpečuje spracovanie interpret testov
 * @param $test - Testovací objekt
 * @param $script - Objekt združujúci informácie o python skripte
 * @return TestProcess
 */
function process_interpret_test($test, $script): TestProcess {

    $process_name = $test->getTestName();
    $process_type = "interpret";

    $src_file = $test->getTestFilePath().".src";

    $out_file = $test->getTestFilePath().".tmp_int_out";
    $err_file = $test->getTestFilePath().".tmp_int_err";
    $input_file = $test->getTestFilePath().".in";
    $out_int_file = $test->getTestFilePath().".out";

    // Vytvorenie testovacieho procesu
    $test_process = new TestProcess($process_type, $process_name, $src_file);

    $test_process->setTmpOutFilePath($out_file);
    $test_process->setTmpErrFilePath($err_file);

    // Vytvorenie python príkazu pre interpret.py
    $python_exec = PYTHON_TAG." ".$script->getIntScriptFile()." --source=".$src_file.
                    " <".$input_file." 2>".$err_file." 1>".$out_file;

    exec($python_exec, $output, $returned_code);

    $test_process->setExpectedExitCode(load_rc_number($test));
    $test_process->setReturnedExitCode($returned_code);

    if ($returned_code != $test_process->getExpectedExitCode()){

        $test_process->setTestPassed(false);
        $script->incFailedTestCount();

        return $test_process;
    }

    // Vytvorenie a spustenie príkazu pre zistenie rozdielov vo výstupoch
    $diff_exec = "diff ".$out_int_file." ".$out_file;
    exec($diff_exec, $output, $returned_code_cmp);

    if ($returned_code_cmp != 0){
        $test_process->setTestPassed(false);
        $script->incFailedTestCount();
    }else{
        $test_process->setTestPassed(true);
        $script->incPassedTestCount();
    }

    return $test_process;

}

/**
 * @brief Funkcia zabezpečuje spracovanie testov parsera a zároveň interpretu
 * @param $test - Testovací objekt
 * @param $script - Objekt združujúci informácie o python skripte
 * @return TestProcess
 */
function process_both_test($test, $script): TestProcess {
    $process_name = $test->getTestName();
    $process_type = "both";

    $parse_src_file = $test->getTestFilePath().".src";
    $parse_out_file = $test->getTestFilePath().".tmp_parse_out";
    $parse_err_file = $test->getTestFilePath().".tmp_parse_err";

    // Vytvorenie php príkazu pre parse.php
    $php_command = PHP_TAG." ".$script->getParseScriptFile()." <".$parse_src_file." 2>".$parse_err_file." 1>".$parse_out_file;

    exec($php_command, $output, $returned_code);

    // Vytvorenie testovacieho procesu
    $test_process = new TestProcess($process_type, $process_name, $parse_src_file);

    if ($returned_code != 0){
        $test_process->setTestPassed(false);
        $script->incFailedTestCount();
        return $test_process;
    }

    $out_file = $test->getTestFilePath().".tmp_int_out";
    $err_file = $test->getTestFilePath().".tmp_int_err";
    $input_file = $test->getTestFilePath().".in";
    $out_int_file = $test->getTestFilePath().".out";

    $test_process->setTmpOutFilePath($out_file);
    $test_process->setTmpErrFilePath($err_file);

    // Vytvorenie python príkazu pre interpret.py
    $python_exec = PYTHON_TAG." ".$script->getIntScriptFile()." --source=".$parse_out_file.
        " <".$input_file." 2>".$err_file." 1>".$out_file;

    exec($python_exec, $output, $returned_code);

    $test_process->setExpectedExitCode(load_rc_number($test));
    $test_process->setReturnedExitCode($returned_code);

    if ($returned_code != $test_process->getExpectedExitCode()){

        $test_process->setTestPassed(false);
        $script->incFailedTestCount();

        return $test_process;
    }

    // Vytvorenie a spustenie príkazu pre zistenie rozdielov vo výstupoch
    $diff_exec = "diff ".$out_int_file." ".$out_file;
    exec($diff_exec, $output, $returned_code_cmp);

    if ($returned_code_cmp != 0){
        $test_process->setTestPassed(false);
        $script->incFailedTestCount();
    }else{
        $test_process->setTestPassed(true);
        $script->incPassedTestCount();
    }

    return $test_process;

}

/**
 * @brief Funkcia ktorá zabezpečuje vymazanie dočasných súborov
 * @param $tests - Testovací objekt
 * @return void
 */
function delete_tmp_files($tests)
{
    $extensions = [".tmp_int_out", ".tmp_int_err", ".tmp_parse_out", ".tmp_parse_err",".tmp_parse_out.log"];
    $files_to_delete = [];
    foreach ($tests as $test) {
        foreach ($extensions as $extension) {
            $files_to_delete[] = $test->getTestFilePath() . $extension;
        }
    }

    foreach ($files_to_delete as $file){
        if(is_file($file)){
            @unlink($file);
        }
    }
}

/**
 * @brief Funkcia zabezpečuje samotné testovanie, generovanie testovacích procesov a generovanie HTML výstupu
 * @param $tests - Zoznam testovacích objektov
 * @param $script - Objekt združujúci informácie o python skripte
 * @return void
 */
function testing($tests, $script){
    $processed_tests = [];

    foreach ($tests as $test){
        $key = $test->getTestFilePath();

        if ($script->isParseTests() and $script->isIntTests()){
            $processed_tests[$key] = process_both_test($test, $script);
            $script->incTotalTestCount();
        }elseif ($script->isParseTests()){
            $processed_tests[$key] = process_parse_test($test, $script);
            $script->incTotalTestCount();

        }elseif ($script->isIntTests()){
            $processed_tests[$key] = process_interpret_test($test, $script);
            $script->incTotalTestCount();
        }
    }

    // Generovanie HTML výstupu
    $script->setPercentage();
    (new Output)->generateTemplate($script, $processed_tests);

    // Vymazávanie dočasných súborov
    if($script->isCleanFiles()){
        delete_tmp_files($tests);
    }
}

