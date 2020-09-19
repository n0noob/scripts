const parseGitURL = (gitDirUrl) => {
  //gitDirUrl = 'https://github.com/n0noob/rest-best-practices/tree/master/src/test/java/com/learn';

  const splitGitUrl = gitDirUrl.split('/');
  let mainGitUrl = '';
  
  if(splitGitUrl.length < 5) {
    throw Error('Not a valid git URL');
  }

  for (let index = 0; index < 5; index++) {
    mainGitUrl += splitGitUrl[index];
    mainGitUrl += '/';
  }
  const gitUrl = `${mainGitUrl.slice(0, mainGitUrl.lastIndexOf('/'))}.git`
  const repoName = splitGitUrl[4];
  let branch;
  let dirPath;
  if(splitGitUrl.length > 5) {
    branch = splitGitUrl[6];
    dirPath = gitDirUrl.slice(gitDirUrl.indexOf(`${branch}`) + branch.length);
  }

  console.log(`Git URL : ${gitUrl}`);
  console.log(`Branch : ${branch}`);
  console.log(`Directory path : ${dirPath}`);

  return {
    gitUrl,
    repoName,
    branch,
    dirPath
  }
}


module.exports = parseGitURL;