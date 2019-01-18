use projectid;


drop table if exists projectid.${VERSION}_dim_pas_lob_test purge;
create table projectid.${VERSION}_dim_pas_lob_test stored as parquet as
select l1_current_lob,l2_current_lob,l3_current_lob,current_lob_cd_leaflabel,lob_cd,leaflkp as dim_pas_lob_leaflkp,current_status_cd,current_status_description
    ,'1900-01-01' as begindt,'2078-12-31' as enddt,iscurrent,leaflkp
from projectid.${PREV_VERSION}_dim_pas_lob
union
select case when lob_cd = 'SOME BKG' then 'PROJECT ACCESS' else concat_ws('-','Unmapped', cast(leaflkp as string)) end as l1_current_lob
        ,case when lob_cd = 'SOME BKG' then 'PROJECT ACCESS' else concat_ws('-','Unmapped', cast(leaflkp as string)) end as l2_current_lob
        ,case when lob_cd = 'SOME BKG' then 'PROJECT ACCESS' else concat_ws('-','Unmapped', cast(leaflkp as string)) end as l3_current_lob
        ,case when lob_cd = 'SOME BKG' then 'PROJECT ACCESS' else concat_ws('-','Unmapped', cast(leaflkp as string)) end as current_lob_cd_leaflabel
        ,lob_cd
             ,leaflkp as dim_pas_lob_leaflkp
        ,case when lob_cd = 'SOME BKG' then 'A' else concat_ws('-','Unmapped', cast(leaflkp as string)) end as current_status_cd
        ,case when lob_cd = 'SOME BKG' then 'Active' else concat_ws('-','Unmapped', cast(leaflkp as string)) end as current_status_description
        ,'1900-01-01' as begindt,'2078-12-31' as enddt,1 as iscurrent,leaflkp
from (    
    select new.lob_cd,cur_dim.cur_mx_leaflkp +row_number() over (order by lob_cd asc) as leaflkp
    from (  
        select distinct pas.lob_cd
        from projectid.${VERSION}_pas_test pas
        where not exists (select 1 from projectid.${PREV_VERSION}_dim_pas_lob dm where dm.lob_cd =pas.lob_cd)
        and isnull(trim(lob_cd),'') <>''
        ) new
    join (select max(leaflkp) as cur_mx_leaflkp from projectid.${PREV_VERSION}_dim_pas_lob) cur_dim on 1=1
) appnd
;
compute stats projectid.${VERSION}_dim_pas_lob_test;
