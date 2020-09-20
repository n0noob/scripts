const simpleGit = require('simple-git');
const fs  = require('fs-extra');
const commandLineArgs = require('command-line-args');
const commandLineUsage = require('command-line-usage');

const parseGitURL = require('./src/utils');
const clObject = require('./src/cl-options');

let inputRemoteDir;
const tempDir = '/tmp';

/* Command line options processing */
const options = commandLineArgs(clObject.optionDefinitions);
const usage = commandLineUsage(clObject.sections);

if( !clObject.validatefields(options) ) {
  console.log(usage);
  return 1;
}
/* Command line options processing ends */

inputRemoteDir = options.url;


(async () => {

  try {
    //Parse Git Dir Url
    const {gitUrl, repoName, branch, dirPath} = parseGitURL(inputRemoteDir);

    //Checkout the code into temporary directory
    let git = await simpleGit();
    await git.cwd(tempDir);
    let gitCloneResult = await git.clone(gitUrl);
    console.log('Cloning complete');

    //Copy the directory to present working directory
    const dirName = dirPath.slice(dirPath.lastIndexOf('/') + 1);
    console.log(`Copy path source : ${dirName}`);
    await fs.copy(`${tempDir}/${repoName}${dirPath}`, `./${dirName}`);
  } catch (err) {
    console.error('Error : ' + err);
  }

})();
