<?php

namespace objects;
class Output
{
    private string $title = "IPP 2022 Testovací skript";


    function generateTemplate($script, $tests)
    {
        echo "<!DOCTYPE html>" . PHP_EOL;
        echo "<html lang='en'>" . PHP_EOL;
        echo "<head>
                <title>" . $this->title . "</title>
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" charset='UTF-8'>
                <!-- Bootstrap -->
                <link href=\"testerFiles/css/bootstrap.css\" rel=\"stylesheet\" media=\"screen\">
             </head>
            " . PHP_EOL;
        echo "<body>" . PHP_EOL;
        echo "    <div class='navbar navbar navbar-dark bg-dark shadow-sm'>
                    <div class='container'>
                        <a href='#' class='navbar-brand d-flex align-items-center'>" . $this->title . "</a>    
                    </div>
                 </div>" . PHP_EOL;
        echo "    <div class='container pt-sm-4 pb-sm-4'>" . PHP_EOL;
        Output::generate_subheader($script);
        foreach ($tests as $test) {
            Output::generate_test($test);
        }
        echo "    </div>" . PHP_EOL;
        echo "</body>" . PHP_EOL;
        echo "</html>" . PHP_EOL;

    }

    static function generate_subheader($script)
    {
        echo "
            <div class='row pb-sm-4'>
                <div class='col-sm-6'>
                    <div class='card h-100'>
                        <h5 class='card-header'>Konfigurácia testov</h5>
                        <div class='card-body'>
                            <p class='card-text'><b>Testovací adresár</b> : " . $script->getDirectoryPath() . "</p>
            " . PHP_EOL;
        if ($script->isRecursive()) {
            echo "<p class='card-text'><b>Rekurzívne prehľadávanie súborov</b> : Zapnuté </p>" . PHP_EOL;
        } else {
            echo "<p class='card-text'><b>Rekurzívne prehľadávanie súborov</b> : Vypnuté </p>" . PHP_EOL;
        }
        if ($script->isCleanFiles()) {
            echo "<p class='card-text'><b>Vymazávanie dočasných súborov</b> : Zapnuté </p>" . PHP_EOL;
        } else {
            echo "<p class='card-text'><b>Vymazávanie dočasných súborov</b> : Vypnuté </p>" . PHP_EOL;
        }

        echo "          </div>
                    </div>
                </div>
                <div class='col-sm-6'>
                    <div class='card h-100'>
                        <h5 class='card-header'>Výsledky testov</h5>
                        <div class='card-body'>
                            <div class='row'>
                                <div class='col-sm-6'>
                                    <p class='card-text'><b>Celkový počet testov</b> : " . $script->getTotalTestCount() . "</p>
                                    <p class='card-text'><b>Počet úspešných testov</b> : " . $script->getPassedTestCount() . "</p>
                                </div>
                                <div class='col-sm-6'>
                                    <p class='card-text'><b>Percentuálny výsledok :</b></p>
                                    <h1>" . $script->getPercentage() . " %</h1>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        " . PHP_EOL;
    }

    static function generate_test($test)
    {
        echo "
        <div class='row pt-2'>
            <div class='col'>
                <div class='card'>
                    <div class='card-header text-white " . ($test->isTestPassed() ? "bg-success" : "bg-danger") . "'>
                        <i style='float: left; padding-right: 2%'><b>Názov testu</b> : " . $test->getName() . "</i>
                        <i style='float: left; padding-right: 2%'><b>Typ testu</b> : " . $test->getType() . "</i>
                    </div>
                    <div class='row'>
                        <div class='col'>
                            <div class='card-body border border-top-0 border-secondary'>
                             " . PHP_EOL;
        echo "<p class='text-dark' ><b>Testovací súbor :</b> ".substr($test->getTestingFile(),0,-4)."</p>".PHP_EOL;
        if ($test->isTestPassed()) {
            echo "<p class='text-dark'>Test prešiel !</p>" . PHP_EOL;
        } else {
            echo "<p class='text-dark'>Test zlyhal !</p>" . PHP_EOL;
            if ($test->getExpectedExitCode() != $test->getReturnedExitCode()) {
                echo "<p class='text-dark'>Očakávaný návratový kód : " . $test->getExpectedExitCode() . "</p>" . PHP_EOL;
                echo "<p class='text-dark'>Získaný návratový kód : " . $test->getReturnedExitCode() . "</p>" . PHP_EOL;
            } else {
                echo "<p class='text-dark'>Rozdielny výstup :</p>" . PHP_EOL;
                $ret_out = file_get_contents($test->getTmpOutFilePath());
                $correct_out = file_get_contents($test->getTestingFile() . ".out");
                echo "<p class='text-dark'>Očakávaný výstup : " . $correct_out . "</p>" . PHP_EOL;
                echo "<p class='text-dark'>Získaný výstup : " . $ret_out . "</p>" . PHP_EOL;
            }
        }
        echo "              </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        " . PHP_EOL;
    }


}