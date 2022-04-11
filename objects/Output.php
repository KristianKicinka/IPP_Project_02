<?php

class Output{
    private String $title = "IPP 2022 Tests";


    function generateTemplate($script, $tests){
       echo "<!DOCTYPE html>".PHP_EOL;
       echo "<html lang='en'>".PHP_EOL;
       echo "<head>
                <title>".$this->title."</title>
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
                <!-- Bootstrap -->
                <link href=\"css/bootstrap.css\" rel=\"stylesheet\" media=\"screen\">
             </head>
            ".PHP_EOL;
       echo "<body>".PHP_EOL;
       echo "    <div class='navbar navbar navbar-dark bg-dark shadow-sm'>
                    <div class='container'>
                        <a href='#' class='navbar-brand d-flex align-items-center'>".$this->title."</a>    
                    </div>
                 </div>".PHP_EOL;
       echo "    <div class='container pt-sm-4 pb-sm-4'>".PHP_EOL;
            Output::generate_subheader($script);
            foreach ($tests as $test){
                Output::generate_test($test);
            }
       echo "    </div>".PHP_EOL;
       echo "</body>".PHP_EOL;
       echo "</html>".PHP_EOL;

    }

    static function generate_subheader($script){
        echo "
            <div class='row pb-sm-4'>
                <div class='col-sm-6'>
                    <div class='card h-100'>
                        <h5 class='card-header'>Testing Configuration</h5>
                        <div class='card-body'>
                            <p class='card-text'><b>Testing directory</b> : ".$script->getDirectoryPath()."</p>
            ".PHP_EOL;
                        if ($script->isRecursive()){
                            echo "<p class='card-text'><b>Recursive scanning files</b> : ON </p>".PHP_EOL;
                        }else{
                            echo "<p class='card-text'><b>Recursive scanning files</b> : OFF </p>".PHP_EOL;
                        }
                        if ($script->isCleanFiles()){
                            echo "<p class='card-text'><b>Cleaning temporary files</b> : ON </p>".PHP_EOL;
                        }else{
                            echo "<p class='card-text'><b>Cleaning temporary files</b> : OFF </p>".PHP_EOL;
                        }

        echo "          </div>
                    </div>
                </div>
                <div class='col-sm-6'>
                    <div class='card h-100'>
                        <h5 class='card-header'>Testing results</h5>
                        <div class='card-body'>
                            <div class='row'>
                                <div class='col-sm-6'>
                                    <p class='card-text'><b>Total tests count</b> : ".$script->getTotalTestCount()."</p>
                                    <p class='card-text'><b>Passed tests</b> : ".$script->getPassedTestCount()."</p>
                                </div>
                                <div class='col-sm-6'>
                                    <p class='card-text'><b>Percentage :</b></p>
                                    <h1>".$script->getPercentage()." %</h1>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        ".PHP_EOL;
    }

    static function generate_test($test){
        echo "
        <div class='row pt-2'>
            <div class='col'>
                <div class='card'>
                    <div class='card-header text-white ".($test->isTestPassed() ? "bg-success" : "bg-danger")."'>
                        <i style='float: left; padding-right: 2%'><b>Test name</b> : ".$test->getName()."</i>
                        <i style='float: left; padding-right: 2%'><b>Test type</b> : ".$test->getType()."</i>
                    </div>
                    <div class='row'>
                        <div class='col'>
                            <div class='card-body border border-top-0 border-secondary'>
                             ".PHP_EOL;
                            if ($test->isTestPassed()){
                                echo "<p class='text-dark'>Test passed !</p>".PHP_EOL;
                            }else{
                                echo "<p class='text-dark'>Test failed !</p>".PHP_EOL;
                                if ($test->getExpectedExitCode() != $test->getReturnedExitCode()){
                                    echo "<p class='text-dark'>Expected exit code : ".$test->getExpectedExitCode()."</p>".PHP_EOL;
                                    echo "<p class='text-dark'>Returned exit code : ".$test->getReturnedExitCode()."</p>".PHP_EOL;
                                }else{
                                    echo "<p class='text-dark'>Different output :</p>".PHP_EOL;
                                    $ret_out = file_get_contents($test->getTmpOutFilePath());
                                    $correct_out = file_get_contents($test->getTestingFile().".out");
                                    echo "<p class='text-dark'>Expected output : ".$correct_out."</p>".PHP_EOL;
                                    echo "<p class='text-dark'>Returned output : ".$ret_out."</p>".PHP_EOL;
                                }
                            }
        echo "              </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        ".PHP_EOL;
    }


}