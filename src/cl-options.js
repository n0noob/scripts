const optionDefinitions = [
  {
    name: 'help',
    description: 'Display this usage guide.',
    alias: 'h',
    type: Boolean
  },
  { 
    name: 'verbose', 
    description: 'Enables verbose mode',
    alias: 'v', 
    type: Boolean 
  },
  { 
    name: 'url',
    description: 'git URL pointing to the remote directory',
    alias: 'u', 
    type: String, 
    defaultOption: true 
  }
];

const sections = [
  {
    header: 'Description',
    content: 'Downloads given {italic remote} directory using git url. '
  },
  {
    header: 'Synopsis',
    content: [
      '$ git-dir {bold --url} {underline url}',
      '$ git-dir {bold --help}'
    ]
  },
  {
    header: 'Options',
    optionList: optionDefinitions
  },
  {
    header: 'Examples',
    content: [
      {
        desc: '1. Download remote directory from git URL ',
        example: '$ git-dir --url https://github.com/exampleorg/example-repo/tree/master/dir1/dir2/dir3'
      }
    ]
  },
];

const validatefields = (parsedOptions) => {
  //Check if url is provided or not
  if( !parsedOptions || !parsedOptions.url) {
    return false;
  }

  //TODO: Check if the url is valid or not

  return true;
}


module.exports = {
  optionDefinitions,
  sections,
  validatefields
}