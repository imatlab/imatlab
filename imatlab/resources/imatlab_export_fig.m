function exported = imatlab_export_fig(exporter)
    % IMATLAB_EXPORT_FIG Set exporter or export figures for imatlab.
    %
    %   IMATLAB_EXPORT_FIG(exporter)
    %     where exporter is one of
    %       {'', 'fig2plotly', 'print-jpeg', 'print-png'}
    %     sets the current exporter.
    %
    %   exported = IMATLAB_EXPORT_FIG
    %     exports the current figures, closes them, and returns a cell array of
    %     exported filenames.

    persistent set_exporter
    if isempty(set_exporter)
        set_exporter = '';
    end
    valid_exporters = {'', 'fig2plotly', 'print-jpeg', 'print-png'};

    if exist('exporter', 'var')
        if any(strcmp(exporter, valid_exporters))
            set_exporter = exporter;
        else
            error(...
                'imatlab:invalidExporter', ...
                ['known exporters are ', ...
                 strjoin(cellfun(@(c) ['''', c, ''''], valid_exporters, ...
                         'UniformOutput', false), ', ')]);
        end
    else
        children = get(0, 'children');
        switch set_exporter
        case ''
            exported = {};
        case 'fig2plotly'
            exported = cell(1, numel(children));
            for i = 1:numel(children)
                name = tempname('.');
                exported{i} = [name, '.html'];
                fig2plotly(children(i), 'filename', name, ...
                           'offline', true, 'open', false);
                close(children(i));
            end
        case 'print-jpeg'
            exported = cell(1, numel(children));
            for i = 1:numel(children)
                name = tempname('.');
                exported{i} = [name, '.jpg'];
                print(children(i), name, '-djpeg');
                close(children(i));
            end
        case 'print-png'
            exported = cell(1, numel(children));
            for i = 1:numel(children)
                name = tempname('.');
                exported{i} = [name, '.png'];
                print(children(i), exported{i}, '-dpng');
                close(children(i));
            end
        end
    end
end
