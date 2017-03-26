function imatlab_set_exporter(exporter, fileType, varargin)
%
% imatlab_set_exporter(exporter, fileType, varargin)
%   sets exporter for imatlab, useful for inline graphics in notebook mode
% Ex:
%   imatlab_set_exporter('fig2plotly');
%   imatlab_set_exporter('print');
%   imatlab_set_exporter('print', '-dtiff', '-r200');
%
% default (with no arguments passed) sets to plotly inline graphics
%
% for 'print' option, file format defaults to png unless specified in fileType
%   varargin parameters will be passed to print in order specified

  fileTypes = { '-djpeg', '-dpng', '-dtiff', '-dtiffn', '-dmeta', '-dbmpmono', ...
                '-dbmp', '-dbmp16m', '-dbmp256', '-dhdf', '-dpbm', '-dpbmraw', ...
                '-dpcxmono', '-dpcx24b', '-dpcx256', '-dpcx16', '-dpgm', '-dpgmraw', ...
                '-dppm', '-dppmraw', '-dpdf', '-deps', '-depsc', '-deps2', '-depsc2', ...
                '-dmeta', '-dsvg', '-dps', '-dpsc', '-dps2', '-dpsc2'; ...
                '.jpg', 'png', 'tif', 'tif', 'emf', '.bmp', '.bmp', '.bmp', '.bmp', ...
                '.hdf', '.pbm', '.pbm', '.pcx', '.pcx.', '.pcx.', '.pcx', ...
                '.pgm', '.pgm', '.ppm', '.ppm', '.pdf', '.eps', '.eps', '.eps', '.eps', ...
                '.emf', '.svg', '.ps', '.ps', '.ps', '.ps'};

  if nargin < 1
    exporter = 'fig2plotly';
  end

  if ~any( strcmp(exporter, {'fig2plotly', 'print'}))
    error('imatlab:imatlab_set_exporter:bad_exporter', 'Invalid exporter specified');
  end


  switch exporter
    case 'fig2plotly'

      setenv('IMATLAB_EXPORT_FIG', func2str(@(h) eval([ ...
             'fig2plotly(h, ''filename'', [tempname(''.''), ''.html''], ', ...
             '''offline'', true, ''open'', false); ', ...
             'close(h);'])));

  case 'print'

    if exist('fileType', 'var')
        fileExt = fileTypes{2, find(strcmp(fileType, fileTypes))};
    else
        fileType = '-dpng';
        fileExt = '.png';
    end


    strOptions = [];
    if ~isempty(varargin)
        for i = 1 : numel(varargin)
            strOptions = [strOptions, ', ', varargin{i}];
        end
    end

    setenv('IMATLAB_EXPORT_FIG', ...
      func2str( @(h) eval([ 'print(h, [tempname(''.''), ''', fileExt, '''], ''', fileType,  '''', strOptions,  ')', 'close(h);'] )) );


  end


end
