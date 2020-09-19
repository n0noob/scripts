const simpleGit = require('simple-git');
const fs  = require('fs-extra');
const parseGitURL = require('./src/utils');

const inputRemoteDir = 'https://github.com/tensorflow/tfjs/tree/master/tfjs-vis/demos/api';
const tempDir = '/tmp';


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
