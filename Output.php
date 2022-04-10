<?php

class Output{
    private String $title = "IPP 2022 Tests";


    function generateTemplate($script){
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
       echo "    <div class='container pt-sm-4'>".PHP_EOL;
            Output::generate_subheader($script);
       echo "    </div>".PHP_EOL;
       echo "</body>".PHP_EOL;
       echo "</html>".PHP_EOL;

    }

    static function generate_subheader($script){
        echo "
            <div class='row'>
                <div class='col-sm-6'>
                    <div class='card'>
                        <h5 class='card-header'>Testing Configuration</h5>
                        <div class='card-body'>
                            <p class='card-text'><b>Testing directory</b> : ".$script->getDirectoryPath()."</p>
            ".PHP_EOL;
                        if ($script->isRecursive()){
                            echo "<p class='card-text'><b>Recursive scanning files</b> : ON </p>".PHP_EOL;
                        }else{
                            echo "<p class='card-text'><b>Recursive scanning files</b> : OFF </p>".PHP_EOL;
                        }

        echo "          </div>
                    </div>
                </div>
                <div class='col-sm-6'>
                    <div class='card'>
                        <h5 class='card-header'>Testing results</h5>
                        <div class='card-body'>
                            <div class='row'>
                                <div class='col-sm-6'>
                                    <p class='card-text'><b>Total tests count</b> : ".$script->getTotalTestCount()."</p>
                                    <p class='card-text'><b>Passed tests</b> : ".$script->getPassedTestCount()."</p>
                                </div>
                                <div class='col-sm-6'>
                                    <p class='card-text'><b>Percentage :</b></p>
                                    <h1>".$script->getPercentage()."</h1>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        ".PHP_EOL;
    }


}